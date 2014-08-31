package pl.edu.mimuw.nesc.analysis.type;

import pl.edu.mimuw.nesc.declaration.tag.StructDeclaration;
import static com.google.common.base.Preconditions.checkArgument;

/**
 * Reflects a non-external structure, e.g.
 * <code>struct S { int n; unsigned int p; }</code>
 *
 * @author Michał Ciszewski <michal.ciszewski@students.mimuw.edu.pl>
 */
public final class StructureType extends MaybeExternalTagType<StructDeclaration> {
    /**
     * Initializes this structure type with given parameters.
     *
     * @param structDeclaration Structure declaration that actually depicts
     *                          this structure type.
     * @throws NullPointerException <code>structDeclaration</code> is null.
     * @throws IllegalArgumentException The given structure declaration
     *                                  represents an external structure.
     */
    public StructureType(boolean constQualified, boolean volatileQualified,
                         StructDeclaration structDeclaration) {
        super(constQualified, volatileQualified, structDeclaration);
        checkArgument(!structDeclaration.isExternal(), "the structure must not be external");
    }
}
