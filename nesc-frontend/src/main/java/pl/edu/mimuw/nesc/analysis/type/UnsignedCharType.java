package pl.edu.mimuw.nesc.analysis.type;

/**
 * @author Michał Ciszewski <michal.ciszewski@students.mimuw.edu.pl>
 */
public final class UnsignedCharType extends UnsignedIntegerType {
    public UnsignedCharType(boolean constQualified, boolean volatileQualified) {
        super(constQualified, volatileQualified);
    }

    @Override
    public final boolean isCharacterType() {
        return true;
    }
}
