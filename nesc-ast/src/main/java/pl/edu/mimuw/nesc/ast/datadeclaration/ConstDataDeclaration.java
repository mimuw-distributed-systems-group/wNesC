package pl.edu.mimuw.nesc.ast.datadeclaration;


public class ConstDataDeclaration extends DataDeclaration {

	public ConstDataDeclaration(String name) {
		super(name);
		// TODO Auto-generated constructor stub
	}

	@Override
	public <R, A> R accept(Visitor<R, A> visitor, A arg) {
		return visitor.visit(this, arg);
	}
}
