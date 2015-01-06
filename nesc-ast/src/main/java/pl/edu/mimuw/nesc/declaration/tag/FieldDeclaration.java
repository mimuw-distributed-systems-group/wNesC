package pl.edu.mimuw.nesc.declaration.tag;

import com.google.common.base.Objects;
import com.google.common.base.Optional;
import pl.edu.mimuw.nesc.type.Type;
import pl.edu.mimuw.nesc.ast.Location;
import pl.edu.mimuw.nesc.declaration.Declaration;

import static com.google.common.base.Preconditions.checkNotNull;

/**
 * @author Grzegorz Kołakowski <gk291583@students.mimuw.edu.pl>
 * @author Michał Ciszewski <michal.ciszewski@students.mimuw.edu.pl>
 */
public class FieldDeclaration extends Declaration {

    /**
     * May be absent for bitfields.
     */
    private final Optional<String> name;

    /**
     * End location of this field.
     */
    private final Location endLocation;

    /**
     * Type of the value in this field. Never null. The value shall be absent
     * if and only if the type of this fields that has been specified is
     * invalid.
     */
    private final Optional<Type> maybeType;

    /**
     * <code>true</code> if and only if this object represents a bit-field.
     */
    private final boolean isBitField;

    public FieldDeclaration(Optional<String> name, Location startLocation, Location endLocation,
                            Optional<Type> type, boolean isBitField) {
        super(startLocation);
        checkNotNull(endLocation, "end location of a field cannot be null");
        checkNotNull(type, "type of a field cannot be null");

        this.name = name;
        this.endLocation = endLocation;
        this.maybeType = type;
        this.isBitField = isBitField;
    }

    public Optional<String> getName() {
        return name;
    }

    public Location getLocation() {
        return location;
    }

    public Location getEndLocation() {
        return endLocation;
    }

    public Optional<Type> getType() {
        return maybeType;
    }

    public boolean isBitField() {
        return isBitField;
    }

    @Override
    public int hashCode() {
        return 31 * super.hashCode() + Objects.hashCode(name);
    }

    @Override
    public boolean equals(Object obj) {
        if (this == obj) {
            return true;
        }
        if (obj == null || getClass() != obj.getClass()) {
            return false;
        }
        if (!super.equals(obj)) {
            return false;
        }
        final FieldDeclaration other = (FieldDeclaration) obj;
        return Objects.equal(this.name, other.name);
    }
}
