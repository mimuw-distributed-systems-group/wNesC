package pl.edu.mimuw.nesc.facade.component.reference;

import com.google.common.base.Optional;
import com.google.common.collect.ImmutableSet;
import java.util.Map;
import pl.edu.mimuw.nesc.declaration.object.ConstantDeclaration;

/**
 * <p>Interface with operations related to obtaining information about
 * declarations of specifications of components.</p>
 *
 * @author Michał Ciszewski <michal.ciszewski@students.mimuw.edu.pl>
 */
public interface ComponentRefFacade {
    /**
     * <p>Check if the component reference is correct, i.e. the referred
     * component exists, has been successfully parsed and analyzed and if it is
     * generic, then all parameters are correctly given.</p>
     *
     * @return <code>true</code> if and only if the reference to the component
     *         is valid.
     */
    boolean goodComponentRef();

    /**
     * <p>Get name of the referred component.</p>
     *
     * @return Name of the referred component.
     */
    String getComponentName();

    /**
     * <p>Get the name of the component used to refer to it in
     * the configuration.</p>
     *
     * @return Name used to refer to the component in the configuration.
     */
    String getInstanceName();

    /**
     * <p>Check if the specification of the referred component contains a type
     * definition with given name. If so, the object is present and the type is
     * nested in it. If the type is present, it is after performing all
     * necessary substitutions.</p>
     *
     * @param name Name of the type definition to lookup.
     * @return The object is present if the specification contains a type
     *         definition with the given name. If the type in the object is
     *         present, it is after all substitutions.
     * @throws NullPointerException Name is null.
     * @throws IllegalArgumentException Name is an empty string.
     */
    Optional<Typedef> getTypedef(String name);

    /**
     * <p>Check if the specification of the referred component contains an
     * enumeration constant with given name. If so, an object that represents
     * the constant is returned. It is the same instance that represents the
     * object in the symbol table.</p>
     *
     * @param name Name of the enumeration constant.
     * @return Object that represents the enumeration constant with give name.
     *         If such constant does not exist, the object is absent.
     * @throws NullPointerException Name is null.
     * @throws IllegalArgumentException Name is an empty string.
     */
    Optional<ConstantDeclaration> getEnumerationConstant(String name);

    /**
     * <p>Get the object that depicts an interface reference or a bare command
     * or event with given name in the referred component. All types provided by
     * the returned object (if present) are after performing all necessary type
     * substitutions.</p>
     *
     * @param name Name of the interface reference or a bare command or event.
     * @return Object that depicts the interface reference or a bare command or
     *         event with given name. It is absent if the specification of the
     *         referred component does not contain any interface or bare command
     *         or event with given name.
     */
    Optional<SpecificationEntity> get(String name);

    /**
     * <p>Get a set with all interfaces and bare commands and events that are
     * declared in the specification of the referred component. All types in
     * <code>SpecificationEntity</code> objects are after all necessary
     * substitutions.</p>
     *
     * @return Immutable set with all interfaces and bare commands or events
     *         declared in the specification of the referred component.
     */
    ImmutableSet<Map.Entry<String, SpecificationEntity>> getAll();
}
