package pl.edu.mimuw.nesc.analysis.expressions;

import com.google.common.base.Optional;
import pl.edu.mimuw.nesc.ast.gen.Expression;
import pl.edu.mimuw.nesc.type.Type;
import static com.google.common.base.Preconditions.checkNotNull;

/**
 * Class whose objects contain results of analysis of an expression.
 *
 * @author Michał Ciszewski <michal.ciszewski@students.mimuw.edu.pl>
 */
public class ExprData {
    /**
     * The type of the expression.
     */
    private Type type;

    /**
     * <code>true</code> if and only if the analyzed expression is an
     * lvalue.
     */
    private boolean isLvalue;

    /**
     * <code>true</code> if and only if the analyzed expression designates
     * a bit-field.
     */
    private boolean isBitField;

    /**
     * <code>true</code> if and only if the analyzed expression is a null
     * pointer constant.
     */
    private boolean isNullPointerConstant;

    /**
     * Get the builder for an expression data object.
     *
     * @return Newly created builder that will build an expression data object.
     */
    public static Builder builder() {
        return new Builder();
    }

    /**
     * Initialize this object with information from the builder.
     *
     * @param builder Builder with the information about expression.
     */
    private ExprData(Builder builder) {
        this.type = builder.type;
        this.isLvalue = builder.isLvalue;
        this.isBitField = builder.isBitField;
        this.isNullPointerConstant = builder.isNullPointerConstant;
    }

    /**
     * Get the type of the analyzed expression.
     *
     * @return Type of the expression. Never null.
     */
    public Type getType() {
        return type;
    }

    /**
     * Check if the expression is an lvalue.
     *
     * @return <code>true</code> if and only if the analyzed expression
     *         designates an lvalue.
     */
    public boolean isLvalue() {
        return isLvalue;
    }

    /**
     * Check if the expression designates a bit-field.
     *
     * @return <code>true</code> if and only if the analyzed expression
     *         designates a bit-field.
     */
    public boolean isBitField() {
        return isBitField;
    }

    /**
     * Check if the expression is a null pointer constant.
     *
     * @return <code>true</code> if and only if the analyzed expression is
     *         a null pointer constant.
     */
    public boolean isNullPointerConstant() {
        return isNullPointerConstant;
    }

    /**
     * <p>Check if this data object depicts a modifiable lvalue. A modifiable
     * lvalue is an lvalue that fulfills all of the conditions:</p>
     * <ul>
     *     <li>does not have array type</li>
     *     <li>does not have an incomplete type</li>
     *     <li>does not have a const-qualified type</li>
     *     <li>if it is a field tag type, does not have any member with
     *     <code>const</code> qualifier (recursively including elements of
     *     arrays and fields of other contained structures or unions)</li>
     * </ul>
     *
     * @return <code>true</code> if and only if this object depicts a modifiable
     *         lvalue.
     */
    public boolean isModifiableLvalue() {
        return isLvalue && !type.isArrayType() && type.isModifiable();
    }

    /**
     * <p>If this data object depicts an lvalue that does not have array type,
     * the lvalue conversion is performed, equivalent to invoking
     * {@link ExprData#lvalueConversion} method. Otherwise, the decaying
     * procedure is done and it has the same effects as if
     * {@link ExprData#decay} method was called.</p>
     *
     * @return <code>this</code>
     */
    ExprData superDecay() {
        if (isLvalue && !type.isArrayType()) {
            lvalueConversion();
        } else {
            decay();
        }

        return this;
    }

    /**
     * <p>Performs the operation of decaying an array object or a function
     * designator.</p>
     * <p>If the type contained in this data object is not an array type and is
     * not a function type, this method does nothing. However, if it is, the
     * following changes are made:</p>
     * <ul>
     *     <li>the type is changed to the type that is the result of decaying it
     *     </li>
     *     <li>lvalue flag is cleared</li>
     * </ul>
     *
     * @return <code>this</code>
     */
    ExprData decay() {
        if (type.isArrayType() || type.isFunctionType()) {
            type = type.decay();
            isLvalue = false;
        }

        return this;
    }

    /**
     * <p>Performs the operation of lvalue conversion. If the data in this
     * object depicts an lvalue that does not have array type, the data are
     * changed in the following way:</p>
     * <ul>
     *     <li>the flag about being lvalue is cleared</li>
     *     <li>the type is changed to the unqualified version of the same
     *     type</li>
     * </ul>
     * <p>Otherwise, this method does nothing.</p>
     *
     * @return <code>this</code>
     */
    ExprData lvalueConversion() {
        if (isLvalue && !type.isArrayType()) {
            type = type.removeQualifiers();
            isLvalue = false;
        }

        return this;
    }

    /**
     * Changes the type contained in this data object to the type that is the
     * result of promoting it.
     *
     * @return <code>this</code>
     */
    ExprData promoteType() {
        type = type.promote();
        return this;
    }

    /**
     * <p>Saves information from this data object to the given expression
     * object. It is done only for information that can be saved to given
     * object. Information that are saved:</p>
     * <ul>
     *     <li>type of the expression</li>
     *     <li>information if the expression is an lvalue</li>
     * </ul>
     *
     * @param expr Expression to store the information in.
     * @return <code>this</code>
     * @throws NullPointerException Given argument is null.
     * @see pl.edu.mimuw.nesc.ast.gen.Expression Expression
     */
    ExprData spread(Expression expr) {
        checkNotNull(expr, "expression cannot be null");
        expr.setType(Optional.of(type));
        expr.setIsLvalue(isLvalue);
        return this;
    }

    /**
     * Builder for an expression data.
     *
     * @author Michał Ciszewski <michal.ciszewski@students.mimuw.edu.pl>
     */
    public static final class Builder {
        private Type type;
        private boolean isLvalue;
        private boolean isBitField;
        private boolean isNullPointerConstant;

        /**
         * Restrict the permissions for instantiating a builder.
         */
        private Builder() {
        }

        /**
         * Set the type of the expression data object that will be created.
         *
         * @param type The type to set.
         * @return <code>this</code>
         */
        public Builder type(Type type) {
            this.type = type;
            return this;
        }

        /**
         * Set if the expression is an lvalue.
         *
         * @param isLvalue Value to set.
         * @return <code>this</code>
         */
        public Builder isLvalue(boolean isLvalue) {
            this.isLvalue = isLvalue;
            return this;
        }

        /**
         * Set if the expression designates a bit-field.
         *
         * @param isBitField Value to set.
         * @return <code>this</code>
         */
        public Builder isBitField(boolean isBitField) {
            this.isBitField = isBitField;
            return this;
        }

        /**
         * Set if the expression is a null pointer constant.
         *
         * @param isNullPointerConstant Value to set.
         * @return <code>this</code>
         */
        public Builder isNullPointerConstant(boolean isNullPointerConstant) {
            this.isNullPointerConstant = isNullPointerConstant;
            return this;
        }

        private void validate() {
            checkNotNull(type, "type cannot be null");
        }

        public ExprData build() {
            validate();
            return new ExprData(this);
        }
    }
}
