package pl.edu.mimuw.nesc.symboltable;

import com.google.common.base.Optional;
import org.junit.Before;
import org.junit.Test;
import pl.edu.mimuw.nesc.ast.Location;
import pl.edu.mimuw.nesc.ast.type.Type;
import pl.edu.mimuw.nesc.declaration.object.ObjectDeclaration;
import pl.edu.mimuw.nesc.declaration.object.VariableDeclaration;

import static org.fest.assertions.Assertions.assertThat;

/**
 * @author Grzegorz Kołakowski <gk291583@students.mimuw.edu.pl>
 */
public class DefaultSymbolTableTest {

    private static final String VAR_A = "A";
    private static final String VAR_B = "B";

    private static final Location LOCATION_10_15 = new Location("file_a.nc", 10, 15);
    private static final Location LOCATION_11_12 = new Location("file_a.nc", 11, 12);

    private SymbolTable<ObjectDeclaration> objectTable;

    private ObjectDeclaration variableA;
    private ObjectDeclaration variableB;

    @Before
    public void setUp() throws Exception {
        objectTable = new DefaultSymbolTable<>();
        variableA = new VariableDeclaration(VAR_A, LOCATION_10_15, Optional.<Type>absent());
        variableB = new VariableDeclaration(VAR_B, LOCATION_11_12, Optional.<Type>absent());
    }

    @Test
    public void testAddAndGetSingleScope() {
        assertThat(objectTable.add(VAR_A, variableA)).isTrue();
        assertThat(objectTable.contains(VAR_A)).isTrue();
        assertThat(objectTable.get(VAR_A)).isEqualTo(Optional.of(variableA));
    }

    @Test
    public void testAddAndGetTwoScopes() {
        assertThat(objectTable.add(VAR_A, variableA)).isTrue();
        final SymbolTable<ObjectDeclaration> enclosedObjectTable = new DefaultSymbolTable<>(Optional.of(objectTable));
        assertThat(enclosedObjectTable.add(VAR_B, variableB)).isTrue();

        assertThat(enclosedObjectTable.contains(VAR_A)).isTrue();
        assertThat(enclosedObjectTable.get(VAR_A)).isEqualTo(Optional.of(variableA));
        assertThat(enclosedObjectTable.contains(VAR_B)).isTrue();
        assertThat(enclosedObjectTable.get(VAR_B)).isEqualTo(Optional.of(variableB));
    }

    @Test
    public void tryToRedeclare() {
        assertThat(objectTable.add(VAR_A, variableA)).isTrue();
        final ObjectDeclaration newVariableA = new VariableDeclaration(VAR_A, LOCATION_11_12, Optional.<Type>absent());
        assertThat(objectTable.add(VAR_A, newVariableA)).isFalse();
    }

    @Test
    public void shadow() {
        assertThat(objectTable.add(VAR_A, variableA)).isTrue();
        final SymbolTable<ObjectDeclaration> enclosedObjectTable = new DefaultSymbolTable<>(Optional.of(objectTable));
        final ObjectDeclaration newVariableA = new VariableDeclaration(VAR_A, LOCATION_11_12, Optional.<Type>absent());

        assertThat(enclosedObjectTable.add(VAR_A, newVariableA)).isTrue();
        assertThat(enclosedObjectTable.contains(VAR_A)).isTrue();
        assertThat(enclosedObjectTable.get(VAR_A)).isEqualTo(Optional.of(newVariableA));
    }
}
