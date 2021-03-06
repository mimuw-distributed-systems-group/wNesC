package pl.edu.mimuw.nesc.instantiation;

import com.google.common.base.Function;
import com.google.common.base.Optional;
import com.google.common.collect.FluentIterable;
import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableMap;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.NavigableSet;
import java.util.Set;
import java.util.TreeSet;
import org.apache.log4j.Logger;
import pl.edu.mimuw.nesc.ast.InstantiationOrigin;
import pl.edu.mimuw.nesc.ast.Location;
import pl.edu.mimuw.nesc.ast.gen.*;
import pl.edu.mimuw.nesc.astutil.NescDeclComparator;
import pl.edu.mimuw.nesc.common.util.VariousUtils;
import pl.edu.mimuw.nesc.names.collecting.NescEntityNameCollector;
import pl.edu.mimuw.nesc.names.mangling.CountingNameMangler;
import pl.edu.mimuw.nesc.names.mangling.NameMangler;
import pl.edu.mimuw.nesc.substitution.GenericParametersSubstitution;

import static com.google.common.base.Preconditions.checkArgument;
import static com.google.common.base.Preconditions.checkNotNull;
import static com.google.common.base.Preconditions.checkState;
import static java.lang.String.format;

/**
 * <p>Class that performs the instantiation of generic components.</p>
 *
 * @author Michał Ciszewski <michal.ciszewski@students.mimuw.edu.pl>
 */
public final class InstantiateExecutor {
    /**
     * Logger for instantiate executors.
     */
    private static final Logger LOG = Logger.getLogger(InstantiateExecutor.class);

    /**
     * Function that returns the alias (if it is absent, then name) of the
     * referred component.
     */
    private static final Function<ComponentRef, String> RETRIEVE_COMPONENT_ALIAS = new Function<ComponentRef, String>() {
        @Override
        public String apply(ComponentRef componentRef) {
            checkNotNull(componentRef, "component reference cannot be null");

            return componentRef.getAlias().isPresent()
                    ? componentRef.getAlias().get().getName()
                    : componentRef.getName().getName();
        }
    };

    /**
     * Current path that leads from a non-generic configuration through
     * instantiated generic components. It is used as a stack for DFS algorithm.
     * The only component that is not a result of instantiation is the first
     * component that has been placed on the stack. It is used to detect cycles
     * during the creation of components.
     */
    private final Deque<ConfigurationNode> currentPath = new ArrayDeque<>();

    /**
     * Deque with current instantiation chain.
     */
    private final Deque<InstantiationOrigin> instantiationChain = new ArrayDeque<>();

    /**
     * Immutable map with information about components to process. Keys are
     * names of components and values are data objects associated with them.
     */
    private final ImmutableMap<String, ComponentData> components;

    /**
     * Set that contains instantiated components (new components that previously
     * hasn't existed). It is absent before performing the instantiation.
     */
    private Optional<NavigableSet<Component>> instantiatedComponents = Optional.absent();

    /**
     * Set to accumulate newly created components.
     */
    private final NavigableSet<Component> componentsAccumulator = new TreeSet<>(new NescDeclComparator());

    /**
     * Component name mangler used to create unique names for instantiated
     * components.
     */
    private final CountingNameMangler componentNameMangler;

    /**
     * Function used for remangling names in instantiated components.
     */
    private final Function<String, String> remanglingFunction;

    /**
     * Get a builder that will create an instantiate executor.
     *
     * @return Newly created builder of an instantiate executor.
     */
    public static Builder builder() {
        return new Builder();
    }

    /**
     * Initializes this executor with information provided by the builder.
     *
     * @param builder Builder with necessary information.
     */
    private InstantiateExecutor(Builder builder) {
        this.components = builder.buildComponentsMap();
        this.componentNameMangler = builder.buildMangler();
        this.remanglingFunction = builder.buildRemanglingFunction();
    }

    /**
     * <p>Performs the instantiation of all generic components that are
     * created in components that have been added to the builder. References
     * to generic parameters of instantiated components are replaced with
     * provided types and expressions in <code>new</code> construct.</p>
     *
     * <p>The given components are modified to correctly refer to instantiated
     * components.</p>
     *
     * @return Set with new components, created as the result of instantiation.
     */
    public NavigableSet<Component> instantiate() throws CyclePresentException {
        if (instantiatedComponents.isPresent()) {
            return instantiatedComponents.get();
        }

        componentsAccumulator.clear();
        currentPath.clear();
        instantiationChain.clear();

        // Loop over all components and start paths in non-generic configurations
        for (ComponentData componentData : components.values()) {
            final Component currentComponent = componentData.getComponent();

            if (!currentComponent.getIsAbstract() && currentComponent instanceof Configuration) {
                instantiateFor(componentData);
            } else {
                LOG.debug("Skipping component '" + currentComponent.getName().getName() + "'");
            }
        }

        instantiatedComponents = Optional.of(componentsAccumulator);
        return componentsAccumulator;
    }

    private void instantiateFor(ComponentData configurationData) throws CyclePresentException {
        final String configurationName = configurationData.getComponent().getName().getName();
        LOG.debug("Starting instantiation of components for '" + configurationName + "'");

        // Place the starting configuration on the stack
        currentPath.addLast(ConfigurationNode.forStartConfiguration(configurationData));
        instantiationChain.addLast(InstantiationOrigin.forFirstElement(configurationName));

        // Perform the instantiation
        while (!currentPath.isEmpty()) {
            final Optional<ComponentRef> nextReference = currentPath.getLast().nextComponentRef();

            if (nextReference.isPresent() && nextReference.get().getIsAbstract()) {
                performComponentInstantiation(nextReference.get(),
                        currentPath.getLast().getConfigurationImpl());
            } else if (!nextReference.isPresent()) {
                final ConfigurationNode lastNode = currentPath.removeLast();
                instantiationChain.removeLast();
                lastNode.getComponentData().setCurrentlyInstantiated(false);
                logPath();
            } else {
                LOG.trace(format("Skipping component reference '%s'",
                        RETRIEVE_COMPONENT_ALIAS.apply(nextReference.get())));
            }
        }

        LOG.debug("Instantiation of components for '" + configurationName + "' successfully ended");
    }

    private void performComponentInstantiation(ComponentRef genericRef,
                ConfigurationImpl implementationToUpdate) throws CyclePresentException {
        // Locate the new component
        final Optional<ComponentData> optInstantiatedComponentData =
                Optional.fromNullable(components.get(genericRef.getName().getName()));
        if (!optInstantiatedComponentData.isPresent()) {
            throw new IllegalStateException("unknown component '" + genericRef.getName().getName()
                    + "' is instantiated");
        }
        final ComponentData instantiatedComponentData = optInstantiatedComponentData.get();

        // Check if there is no cycle
        checkState(instantiatedComponentData.getComponent().getIsAbstract(), "instantiating non-generic component '%s'",
                genericRef.getName().getName());
        if (instantiatedComponentData.isCurrentlyInstantiated()) {
            throw CyclePresentException.newInstance(currentPath, genericRef.getName().getName());
        }

        instantiationChain.addLast(InstantiationOrigin.forNextElement(genericRef.getName().getName(),
                genericRef.getAlias().or(genericRef.getName()).getName()));

        logInstantiationInfo(genericRef);
        final Component newComponent = copyComponent(instantiatedComponentData.getComponent(),
                genericRef, implementationToUpdate);

        // Update state
        if (!componentsAccumulator.add(newComponent)) {
            throw new RuntimeException("a newly created component unexpectedly present in the components accumulator");
        }
        if (newComponent instanceof Configuration) {
            instantiatedComponentData.setCurrentlyInstantiated(true);
            final ConfigurationNode newNode = ConfigurationNode.forNewConfiguration(instantiatedComponentData,
                    (Configuration) newComponent);
            currentPath.addLast(newNode);
            logPath();
        } else {
            instantiationChain.removeLast();
        }
    }

    /**
     * Copy the given component and make all necessary changes to the copy.
     *
     * @param specimen Generic component that will be copied.
     * @param genericRef Reference to the generic component that causes the copy
     *                   to be created (the <code>new</code> construct).
     * @return Properly modified and prepared copy of the given component.
     */
    private Component copyComponent(Component specimen, ComponentRef genericRef,
                ConfigurationImpl implementationToUpdate) {
        final Map<Node, Node> nodesMap = new HashMap<>();
        final Component copy = specimen.deepCopy(false, Optional.of(nodesMap));
        final RemanglingVisitor manglingVisitor = new RemanglingVisitor(remanglingFunction);
        final SubstitutionManager substitution = GenericParametersSubstitution.forComponent()
                .componentRef(genericRef)
                .genericComponent(specimen)
                .build();
        final ASTFillingVisitor typeDiscoverer = new ASTFillingVisitor(genericRef,
                specimen, substitution, nodesMap, manglingVisitor.getNamesMap());

        copy.setInstantiationChain(Optional.of(ImmutableList.copyOf(instantiationChain)));
        copy.setIsAbstract(false);
        copy.setParameters(Optional.<LinkedList<Declaration>>absent());
        copy.getName().setName(componentNameMangler.mangle(copy.getName().getName()));
        copy.accept(manglingVisitor, null);
        copy.substitute(substitution);
        copy.traverse(typeDiscoverer, null);
        typeDiscoverer.mapOwners();

        if (copy instanceof Module) {
            final Module moduleCopy = (Module) copy;
            moduleCopy.getModuleTable().collectUniqueNames((ModuleImpl) moduleCopy.getImplementation());
        }

        // Change the reference of the component
        genericRef.setIsAbstract(false);
        genericRef.setArguments(new LinkedList<Expression>());
        final String newAlias = genericRef.getAlias().isPresent()
                ? genericRef.getAlias().get().getName()
                : genericRef.getName().getName();
        genericRef.getName().setName(copy.getName().getName());
        genericRef.setAlias(Optional.of(new Word(Location.getDummyLocation(), newAlias)));

        /* Change references to entities in the created components in the source
           configuration. */
        implementationToUpdate.traverse(new ConfigurationImplUpdateVisitor(newAlias, typeDiscoverer), null);

        /* FIXME tag type objects in the source configuration can contain
           objects from the generic component due to 'Substitution' class
           behaviour and setting the substituted type when 'ComponentTyperef'
           is analyzed. */

        return copy;
    }

    private void logPath() {
        if (LOG.isDebugEnabled()) {
            final StringBuilder path = new StringBuilder();
            path.append("Current path: ");

            if (!currentPath.isEmpty()) {
                boolean isFirst = true;

                for (ConfigurationNode node : currentPath) {
                    if (!isFirst) {
                        path.append(" -> ");
                    }
                    path.append(node.getComponentData().getComponent().getName().getName());
                    isFirst = false;
                }
            } else {
                path.append("<empty>");
            }

            LOG.debug(path);
        }
    }

    private void logInstantiationInfo(ComponentRef componentRef) {
        if (LOG.isDebugEnabled()) {
            final String componentRefName = RETRIEVE_COMPONENT_ALIAS.apply(componentRef);
            final String componentName = componentRef.getName().getName();

            if (!componentName.equals(componentRefName)) {
                LOG.debug(format("Instantiating component '%s' aliased as '%s'", componentName,
                        componentRefName));
            } else {
                LOG.debug(format("Instantiating component '%s'", componentName));
            }
        }
    }

    /**
     * Builder for an instantiate executor.
     *
     * @author Michał Ciszewski <michal.ciszewski@students.mimuw.edu.pl>
     */
    public static final class Builder {
        /**
         * Data needed to build an instantiate executor.
         */
        private final List<NescDecl> nescDeclarations = new ArrayList<>();
        private NameMangler nameMangler;

        /**
         * Private constructor to limit its accessibility.
         */
        private Builder() {
        }

        /**
         * Adds the given NesC declaration to take part in the instantiation
         * process.
         *
         * @param nescDecl Interface or component to add.
         * @return <code>this</code>
         */
        public Builder addNescDeclaration(NescDecl nescDecl) {
            this.nescDeclarations.add(nescDecl);
            return this;
        }

        /**
         * Add NesC declarations from the given list of nodes. Only nodes from
         * the given list that represent interfaces and components are added.
         *
         * @param nodes List with nodes (and possibly interfaces and components)
         *              to add.
         * @return <code>this</code>
         */
        public Builder addNescDeclarations(List<? extends Node> nodes) {
            FluentIterable.from(nodes)
                    .filter(NescDecl.class)
                    .copyInto(nescDeclarations);
            return this;
        }

        /**
         * Set the name mangler that will be used to remangle names in
         * instantiated components. It shall be the same mangler used to mangle
         * the original names in generic components.
         *
         * @param nameMangler Name mangler to set.
         * @return <code>this</code>
         */
        public Builder nameMangler(NameMangler nameMangler) {
            this.nameMangler = nameMangler;
            return this;
        }

        private void validate() {
            final Set<String> names = new HashSet<>();

            for (NescDecl nescDecl : nescDeclarations) {
                checkNotNull(nescDecl, "null has been added as an interface or component");

                if (!names.add(nescDecl.getName().getName())) {
                    throw new IllegalStateException("names of added NesC declarations are not unique");
                }
            }

            checkNotNull(nameMangler, "name mangler not set or set to null");
        }

        public InstantiateExecutor build() {
            validate();
            return new InstantiateExecutor(this);
        }

        private ImmutableMap<String, ComponentData> buildComponentsMap() {
            final ImmutableMap.Builder<String, ComponentData> builder = ImmutableMap.builder();
            final FluentIterable<Component> components = FluentIterable.from(nescDeclarations)
                    .filter(Component.class);

            for (Component component : components) {
                if (component instanceof BinaryComponent) {
                    continue;
                }

                builder.put(component.getName().getName(), new ComponentData(component));
            }

            return builder.build();
        }

        private CountingNameMangler buildMangler() {
            final NescEntityNameCollector nameCollector = new NescEntityNameCollector();
            nameCollector.collect(nescDeclarations);
            return new CountingNameMangler(nameCollector.get());
        }

        private Function<String, String> buildRemanglingFunction() {
            return new Function<String, String>() {
                private final NameMangler mangler;

                {
                    /* Force using the mangler that is currently assigned in the
                       builder so that potential further changes in the builder
                       will not affect the returned remangling function. */
                    this.mangler = Builder.this.nameMangler;
                }

                @Override
                public String apply(String mangledName) {
                    return this.mangler.remangle(mangledName);
                }
            };
        }
    }

    /**
     * Visitor that updates data in component type references and component
     * dereferences AST nodes that refer to an entity in currently
     * instantiated component.
     *
     * @author Michał Ciszewski <michal.ciszewski@students.mimuw.edu.pl>
     */
    private static final class ConfigurationImplUpdateVisitor extends IdentityVisitor<Void> {
        private final String componentRefName;
        private final ASTFillingVisitor fillingVisitor;

        private ConfigurationImplUpdateVisitor(String componentRefName, ASTFillingVisitor fillingVisitor) {
            checkNotNull(componentRefName, "component reference name cannot be null");
            checkNotNull(fillingVisitor, "the filling visitor cannot be null");
            checkArgument(!componentRefName.isEmpty(), "component reference name cannot be null");

            this.componentRefName = componentRefName;
            this.fillingVisitor = fillingVisitor;
        }

        @Override
        public Void visitComponentTyperef(ComponentTyperef typeref, Void arg) {
            if (isUpdateRequired(typeref)) {
                fillingVisitor.mapComponentTyperef(typeref);
            }
            return null;
        }

        @Override
        public Void visitComponentDeref(ComponentDeref deref, Void arg) {
            if (isUpdateRequired(deref)) {
                fillingVisitor.mapComponentDeref(deref);
            }
            return null;
        }

        private boolean isUpdateRequired(ComponentTyperef typeref) {
            return typeref.getName().equals(componentRefName)
                    && !VariousUtils.getBooleanValue(typeref.getIsPasted());
        }

        private boolean isUpdateRequired(ComponentDeref deref) {
            return ((Identifier) deref.getArgument()).getName().equals(componentRefName)
                    && !VariousUtils.getBooleanValue(deref.getIsPasted());
        }
    }
}
