# coding=utf-8
#from ast_core import *
from ast.core import BasicASTNode, generate_code, GenericIndicator, MangleIndicator, \
    UniqueIndicator
from ast.field_copy import DEEP_COPY_MODE
from ast.fields import *

#==============================================================================
#                             
#============================================================================== 

# ===== Naming convention =====
#
# All class names are borrowed from nodetypes.def and adjusted to Java naming
# convention. Class names start with capital letter.
#
# Examples:
#  node -> Node
#  tag_ref -> TagRef
#  asttype -> AstType
#
# Sometimes field or class names collide with language keywords.
#
#    abstract -> isAbstract
#    String -> StringAst
#

#==============================================================================
#                             Selected fields description
#==============================================================================

# ISATOMIC 
#    ATOMIC_ANY if the statement does not involve any shared variable accesses
#    ATOMIC_SINGLE if the statement involves a single access to a shared 
#    variable, and that access is guaranteed to be atomic (e.g., a single byte)
#    NOT_ATOMIC otherwise

#==============================================================================
#                                    Base types
#==============================================================================


class Node(BasicASTNode):
    """ A common superclass of all AST nodes. """
    location = ReferenceField("Location", visitable=False, deep_copy_mode=DEEP_COPY_MODE.ASSIGN_REFERENCE_COPY)
    endLocation = ReferenceField("Location", constructor_variable=False, visitable=False,
                                 deep_copy_mode=DEEP_COPY_MODE.ASSIGN_REFERENCE_COPY)
    next = ReferenceField("Node", constructor_variable=False, visitable=False,
                          deep_copy_mode=DEEP_COPY_MODE.ASSIGN_NULL)
    isPasted = BoolField(constructor_variable=False)


class Declaration(BasicASTNode):
    """ A common superclass of all definitions. """
    superclass = Node
    genericIndicator = GenericIndicator()


# TODO: statements probably should have pointer to the next statement,
class Statement(BasicASTNode):
    """ A common superclass of all statements. """
    superclass = Node
    # FIXME: the fields below are borrowed from ncc, but they are propably not required in our implementation.
    # PARENT_LOOP
    # - for break and continue: the containing for/while/do-while/switch
    # statement they escape from.
    # - for for/while/do-while: the containing for/while/do-while/switch
    # statement.
    # parentLoop = ReferenceField("Statement", constructor_variable=False, visitable=False)
    # CONTAINING_ATOMIC
    # - for return statement: their containing atomic statement
    # - for labels and looping statements, their containing atomic statement
    # (or NULL for none). Used to check that break, continue and goto do not
    # break in or out of an atomic statement.
    # (Note: for nested atomic statements, CONTAINING_ATOMIC will point to a
    # dangling node as we drop these nested statements from the AST).
    # containingAtomic = ReferenceField("AtomicStmt", constructor_variable=False, visitable=False)
    # See section: Selected fields description.
    # isAtomic = ReferenceField("AtomicType", constructor_variable=False, visitable=False)


class Expression(BasicASTNode):
    """
    <p>A common superclass of all expressions.</p>
    <p><code>parenthesesCount</code> is the number of parentheses that surround the
    expression directly. If no parentheses surround it, it is <code>null</code> or zero.
    This field is relevant when generating error messages.</p>
    <p><code>isNxTransformed</code> is <code>true</code> if this expression does
    not need any further transformations that are related to reading values of
    external base types.</p>
    """
    superclass = Node
    genericIndicator = GenericIndicator()
    type = ReferenceField("Type", optional=True, constructor_variable=False, deep_copy_mode=DEEP_COPY_MODE.ASSIGN_REFERENCE_COPY)
    parenthesesCount = IntField(constructor_variable=False, deep_copy_mode=DEEP_COPY_MODE.ASSIGN_REFERENCE_COPY)
    isLvalue = BoolField(constructor_variable=False)
    isNxTransformed = BoolField(constructor_variable=False)
    # FIXME: the fields below are borrowed from ncc, but they are propably not required in our implementation.
    # LVALUE is true if this expression can be used in a context requiring an
    # lvalue.
    #lvalue = BoolField(constructor_variable=False, visitable=False)
    # SIDE_EFFECTS is true if the expression has side effects.
    #sideEffects = BoolField(constructor_variable=False, visitable=False)
    # CST is non-null (and points to an appropriate constant) if this
    # expression is constant.
    #cst = ReferenceField("KnownCst", constructor_variable=False, visitable=False)
    # BITFIELD is true if this lvalue is a bitfield.
    #bitfield = BoolField(constructor_variable=False, visitable=False)
    # ISREGISTER is true if this lvalue is (declared to be) in a register.
    #isRegister = BoolField(constructor_variable=False, visitable=False)

    # STATIC_ADDRESS is true for lvalues whose address is a constant
    # expression.
    #staticAddress = ReferenceField("KnownCst", constructor_variable=False, visitable=False)
    # CONVERTED_TO_POINTER is true for expressions which default_conversion
    # indicates need converting to pointer type (note that these nodes did not
    # have their type changed).
    #convertedToPointer = BoolField(constructor_variable=False, visitable=False)
    # CST_CHECKED is set to true once we've successfully checked this
    # expression's constantness, and associated constant value (used to avoid
    # duplicate error messages in repeated constant folding passes).
    #cstChecked = BoolField(constructor_variable=False, visitable=False)
    # SPELLING saves the `spelling' (a user-friendly name) of expressions used
    # in initialisers.
    #spelling = StringField(constructor_variable=False, visitable=False)
    # PARENS is TRUE if the expression is in parentheses
    #parens = BoolField(constructor_variable=False, visitable=False)
    # IVALUE is a pointer to an ivalue (see init.h) holding the value of an
    # initialiser expression. On an init_list or in an expression used as
    # a simple initialiser (e.g., '3 + 2' in 'int x = 3 + 2'), this is the
    # value of the initialiser. Inside these initialisers, ivalue points into
    # the ivalue structure of the containing initialiser.
    #ivalue = ReferenceField("IValue", constructor_variable=False, visitable=False)
    # CONTEXT is the usage context for this expression (see nesc-uses.h).
    #context = ReferenceField("Context", constructor_variable=False, visitable=False)
    # See section: Selected fields description.
    #isAtomic = ReferenceField("AtomicType", constructor_variable=False, visitable=False)


class TypeElement(BasicASTNode):
    """ A common superclass for all type-building elements (qualifiers, modifiers, attributes, etc.). """
    superclass = Node


class Declarator(BasicASTNode):
    """ A common superclass for all declarators. """
    superclass = Node


class Label(BasicASTNode):
    """
    <p>A common superclass for all labels.</p>
    <p><code>nextLabel</code> points to the next case or default label of a switch (for case or default labels only).
    </p>
    """
    superclass = Node
    nextLabel = ReferenceField("Label", constructor_variable=False, visitable=False,
                               deep_copy_mode=DEEP_COPY_MODE.ASSIGN_NULL)


#==============================================================================
#                                 Declarations
#==============================================================================

class ErrorDecl(BasicASTNode):
    """ Placeholder for erroneous declarations. """
    superclass = Declaration


class EmptyDecl(BasicASTNode):
    """ Empty declaration. Represents a redundant semicolon after declaration chain. """
    superclass = Declaration


class AsmDecl(BasicASTNode):
    """
    <p>Asm declaration. GNU extension.</p>
    """
    superclass = Declaration
    asmStmt = ReferenceField("AsmStmt")


# The declaration MODIFIERS DECLS; DECLS is a list.
# TODO: description
class DataDecl(BasicASTNode):
    superclass = Declaration
    modifiers = ReferenceListField("TypeElement")
    declarations = ReferenceListField("Declaration")
    type = ReferenceField("Type", optional=True, constructor_variable=False, deep_copy_mode=DEEP_COPY_MODE.ASSIGN_NULL)


class ExtensionDecl(BasicASTNode):
    """
    GCC uses the __extension__ attribute when using the -ansi flag to avoid warnings in headers with GCC extensions.
    This is mostly used in glibc with function declarations using long long.
    """
    superclass = Declaration
    declaration = ReferenceField("Declaration")


class EllipsisDecl(BasicASTNode):
    """ # A pseudo-declaration to represent ... in a function argument list. """
    superclass = Declaration


class Enumerator(BasicASTNode):
    """ The enumeration element. """
    superclass = Declaration
    mangleIndicator = MangleIndicator("uniqueName", "nestedInNescEntity")
    # name is optional.
    name = StringField()
    value = ReferenceField("Expression", optional=True)
    declaration = ReferenceField("ConstantDeclaration", constructor_variable=False, visitable=False,
                                 deep_copy_mode=DEEP_COPY_MODE.ASSIGN_REFERENCE_COPY)


class OldIdentifierDecl(BasicASTNode):
    """
    Parameter declaration in old-style way (K&R style).

    <pre>
        void f(i, c, fp)
        int i;
        char c;
        float *fp;
        { ... }
    </pre>
    """
    superclass = Declaration
    # CSTRING in an old-style parameter list.
    name = StringField()
    declaration = ReferenceField("VariableDeclaration", constructor_variable=False, visitable=False,
                                 deep_copy_mode=DEEP_COPY_MODE.ASSIGN_REFERENCE_COPY)


class FunctionDecl(BasicASTNode):
    """
    <p>A function declaration.</p>
    <p><code>declaration</code> can be function declaration or interface
    reference.</p>
    <p><code>isAtomic</code> is set to <code>true</code> when all of the
    following conditions are fulfilled:</p>
    <ol>
        <li>the only references of this function in the whole application are
        in function calls</li>
        <li>all calls to this function are made from areas of code that
        is known to execute atomically; an example of such situation is when
        all calls of the function are located inside an atomic block</li>
        <li>call assumptions for this function are NORMAL or ATOMIC_HWEVENT
        </code>
    </ol>
    <p><code>intermediateData</code> is set only if this function is an
    intermediate function and contains the data about the command or event
    it corresponds to.</p>
    """
    superclass = Declaration
    declarator = ReferenceField("Declarator")
    modifiers = ReferenceListField("TypeElement")
    attributes = ReferenceListField("Attribute")
    # OLD_PARMS is the old-style parameter declaration list.
    oldParms = ReferenceListField("Declaration", constructor_variable=False)
    body = ReferenceField("Statement")
    isNested = BoolField(visitable=False)
    declaration = ReferenceField("FunctionDeclaration", constructor_variable=False, visitable=False,
                                 deep_copy_mode=DEEP_COPY_MODE.ASSIGN_REFERENCE_COPY)
    isAtomic = BoolField(constructor_variable=False)
    intermediateData = ReferenceField("IntermediateData", constructor_variable=False, visitable=False,
                                      deep_copy_mode=DEEP_COPY_MODE.ASSIGN_NULL, optional=True)

    # FIXME refactor attributes below
    #parentFunction = ReferenceField("FunctionDecl", constructor_variable=False, visitable=False)
    #fdeclarator = ReferenceField("FunctionDeclarator", constructor_variable=False, visitable=False)
    #declaredType = ReferenceField("Type", constructor_variable=False, visitable=False)
    #undeclaredVariables = ReferenceField("Env", constructor_variable=False, visitable=False)
    #baseLabels = ReferenceField("Env", constructor_variable=False, visitable=False)
    #scopedLabels = ReferenceField("Env", constructor_variable=False, visitable=False)
    #currentLoop = ReferenceField("Statement", constructor_variable=False, visitable=False)
    #nlocals = IntField(constructor_variable=False, visitable=False)


# Used as the AST node for implicit declarations.
class ImplicitDecl(BasicASTNode):
    superclass = Declaration
    # IDENT points to the identifier node that implicitly declared the function.
    ident = ReferenceField("Identifier")


class VariableDecl(BasicASTNode):
    """
    <p>Declaration of the following syntax:
    <code>declarator asm_stmt attributes [= initializer]</code>.</p>
    <p>The name of the node is misleading, it corresponds not only to a variable declaration, but also to
    a typedef declaration or a function forward declaration.<p>
    """
    superclass = Declaration
    declarator = ReferenceField("Declarator", optional=True)
    attributes = ReferenceListField("Attribute")
    initializer = ReferenceField("Expression", constructor_variable=False, optional=True)
    asmStmt = ReferenceField("AsmStmt", optional=True)
    declaration = ReferenceField("ObjectDeclaration", constructor_variable=False, visitable=False,
                                 deep_copy_mode=DEEP_COPY_MODE.ASSIGN_REFERENCE_COPY)
    type = ReferenceField("Type", optional=True, constructor_variable=False, deep_copy_mode=DEEP_COPY_MODE.ASSIGN_NULL)
    forward = BoolField(constructor_variable=False, visitable=False)


class FieldDecl(BasicASTNode):
    """
    <p>Tag field declaration.</p>
    """
    superclass = Declaration
    declarator = ReferenceField("Declarator", optional=True)
    attributes = ReferenceListField("Attribute")
    bitfield = ReferenceField("Expression", optional=True)
    declaration = ReferenceField("FieldDeclaration", constructor_variable=False, visitable=False,
                                 deep_copy_mode=DEEP_COPY_MODE.ASSIGN_REFERENCE_COPY)


#==============================================================================
#                           Types and type elements
#==============================================================================

# The source-level type QUALIFIERS DECLARATOR.
class AstType(BasicASTNode):
    superclass = Node
    genericIndicator = GenericIndicator()
    declarator = ReferenceField("Declarator", optional=True)
    qualifiers = ReferenceListField("TypeElement")
    type = ReferenceField("Type", optional=True, constructor_variable=False, deep_copy_mode=DEEP_COPY_MODE.ASSIGN_REFERENCE_COPY)


# typedef-type with declaration DDECL. The name is ddecl->name.
class Typename(BasicASTNode):
    """
    <p><code>isGenericReference</code> is set to <code>true</code> after the semantic analysis if and only
    if this typename occurs inside a generic component definition and refers to one of its generic type
    parameters.</p>
    <p>If <code>hasAtomicOrigin</code> is set to <code>true</code>, this AST node has been created as the
    result of atomic unfolding.</p>
    """
    superclass = TypeElement
    mangleIndicator = MangleIndicator("uniqueName", "isDeclaredInThisNescEntity")
    name = StringField()
    isGenericReference = BoolField(constructor_variable=False)
    hasAtomicOrigin = BoolField(constructor_variable=False)
    declaration = ReferenceField("TypenameDeclaration", constructor_variable=False, visitable=False,
                                 deep_copy_mode=DEEP_COPY_MODE.ASSIGN_REFERENCE_COPY)


# typeof ARG1
class TypeofExpr(BasicASTNode):
    superclass = TypeElement
    expression = ReferenceField("Expression")


# typeof(ASTTYPE)
class TypeofType(BasicASTNode):
    superclass = TypeElement
    asttype = ReferenceField("AstType")


# base type for gcc and nesc attributes.
class Attribute(BasicASTNode):
    superclass = TypeElement
    name = ReferenceField("Word")


# The (gcc) attribute WORD1(ARGS).
class GccAttribute(BasicASTNode):
    """
    <p>GCC attribute.</p>
    <p><code>arguments</code> of attribute may be empty and may not be semantically valid.</p>
    """
    superclass = Attribute
    arguments = ReferenceListField("Expression", optional=True)


# Storage class specifier, type specifier or type qualifier ID (see RID_xxx)
class Rid(BasicASTNode):
    superclass = TypeElement
    id = ReferenceField("RID", deep_copy_mode=DEEP_COPY_MODE.ASSIGN_REFERENCE_COPY)


# Type or function qualifier ID (see qualifiers.h and type_quals in types.h)
class Qualifier(BasicASTNode):
    superclass = TypeElement
    id = ReferenceField("RID", deep_copy_mode=DEEP_COPY_MODE.ASSIGN_REFERENCE_COPY)


class TagRef(BasicASTNode):
    """
    <p>A reference to a tag in a declaration.</p>
    <p>The meaning of individual values in <code>semantics</code> field is given in the definition
    of <code>TagRefSemantics</code> enumeration type. In particular, one can check if this object
    represents a definition by reading the value of the field.</p>
    <p><code>isInvalid</code> field is meaningful only after semantic analysis of a tag
    reference. When the analysis is done, <code>isInvalid</code> is <code>true</code> if and only if
    the tag reference is invalid semantically, e.g. it conflicts with a previous declaration.</p>
    """
    superclass = TypeElement
    mangleIndicator = MangleIndicator("uniqueName", "nestedInNescEntity", optional=True)
    name = ReferenceField("Word")   # FIXME optional!
    attributes = ReferenceListField("Attribute")
    fields = ReferenceListField("Declaration")  # FIXME optional!
    semantics = ReferenceField("StructSemantics", deep_copy_mode=DEEP_COPY_MODE.ASSIGN_REFERENCE_COPY)
    isInvalid = BoolField(constructor_variable=False)


# A struct
class StructRef(BasicASTNode):
    """
    <p>A struct.</p>
    """
    superclass = TagRef
    declaration = ReferenceField("StructDeclaration", constructor_variable=False, visitable=False,
                                 deep_copy_mode=DEEP_COPY_MODE.ASSIGN_REFERENCE_COPY)


# An attribute definition.
# FIXME what does this node represents?
class AttributeRef(BasicASTNode):
    superclass = TagRef
    declaration = ReferenceField("AttributeDeclaration", constructor_variable=False, visitable=False,
                                 deep_copy_mode=DEEP_COPY_MODE.ASSIGN_REFERENCE_COPY)


# A union
class UnionRef(BasicASTNode):
    superclass = TagRef
    declaration = ReferenceField("UnionDeclaration", constructor_variable=False, visitable=False,
                                 deep_copy_mode=DEEP_COPY_MODE.ASSIGN_REFERENCE_COPY)


# An enum
class EnumRef(BasicASTNode):
    superclass = TagRef
    declaration = ReferenceField("EnumDeclaration", constructor_variable=False, visitable=False,
                                 deep_copy_mode=DEEP_COPY_MODE.ASSIGN_REFERENCE_COPY)


#==============================================================================
#                                 Declarators
#==============================================================================

class NestedDeclarator(BasicASTNode):
    """
    <p>A common supertype for function/pointer/array declarator which includes the nested declarator.</p>
    <p> <code>declarator</code> refers to declarator that precedes e.g. function/array parentheses or follows
    pointer asterisk, e.g.:</p>
    <pre>
    foo(int i, int j)
    ^^^
    declarator

    * foo
      ^^^
      declarator
    </pre>

    <p><code>declarator</code> can be absent. Consider the forward declaration with parameters without names
    <code>void f(int*);</code> .</p>
    """
    superclass = Declarator
    declarator = ReferenceField("Declarator", optional=True)


class FunctionDeclarator(BasicASTNode):
    """
    <p>Function declarator. Represents either C function or NesC command/event.</p>
    <p>It consists of:
    <ul>
    <li><code>parameters</code> - list of standard function parameters,</li>
    <li><code>genericParameters</code> - list of generic parameters, present only in NesC command/event,</li>
    <li><code>qualifiers</code> - list of qualifiers,</li>
    <li><code>environment</code> - environment for both kind of function parameters,</li>
    <li><code>isBanked</code> - value indicating if the SDCC keyword <code>__banked</code> is present.</li>
    </ul>
    </p>
    """
    superclass = NestedDeclarator
    parameters = ReferenceListField("Declaration")
    genericParameters = ReferenceListField("Declaration", optional=True)
    qualifiers = ReferenceListField("TypeElement")
    environment = ReferenceField("Environment", constructor_variable=False, visitable=False,
                                 deep_copy_mode=DEEP_COPY_MODE.ASSIGN_NULL)
    isBanked = BoolField(constructor_variable=False)
    #returnType = ReferenceField("AstType", constructor_variable=False, optional=True, visitable=False)


class PointerDeclarator(BasicASTNode):
    """
    Pointer declarator.
    """
    superclass = NestedDeclarator

class QualifiedDeclarator(BasicASTNode):
    """
    A declarator that is preceded by a list of type elements:
    qualifiers or attributes. The list must not be empty.
    """
    superclass = NestedDeclarator
    modifiers = ReferenceListField("TypeElement")


# Array declarator DECLARATOR[ARG1]. ARG1 is optional.
class ArrayDeclarator(BasicASTNode):
    """
    Array declarator. The <code>size</code> is optional.
    """
    superclass = NestedDeclarator
    size = ReferenceField("Expression", optional=True)


class IdentifierDeclarator(BasicASTNode):
    """
    A simple declarator consisting of only a single identifier.
    The unique name is absent if this declarator is used to declare a field in
    a structure or union (either external or not).
    """
    superclass = Declarator
    mangleIndicator = MangleIndicator("uniqueName", "isNestedInNescEntity", optional=True)
    name = StringField()


#==============================================================================
#                                  Statements
#==============================================================================

class ErrorStmt(BasicASTNode):
    """
    Placeholder for erroneous statements.
    """
    superclass = Statement


# TODO: improve description
class AsmStmt(BasicASTNode):
    """
    The statement asm QUALIFIERS (ARG1 : ASM_OPERANDS1 : ASM_OPERANDS2 : ASM_CLOBBERS)
    where ASM_OPERANDS1, ASM_OPERANDS2, QUALIFIERS are optional, ASM_CLOBBERS is a list (GCC)
    """
    superclass = Statement
    arg1 = ReferenceField("Expression")
    asmOperands1 = ReferenceListField("AsmOperand")
    asmOperands2 = ReferenceListField("AsmOperand")
    asmClobbers = ReferenceListField("StringAst")
    qualifiers = ReferenceListField("TypeElement")


class CompoundStmt(BasicASTNode):
    """
    <p>Represents a block with its own environment.</p>
    <p>It can be body of function or statement.</p>
    <p><code>atomicVariableUniqueName</code> is present if and only if this compound statement
    has replaced an atomic statement. Otherwise, it is absent or <code>null</code>. If the
    object is present, it is the unique name of the variable created to store the result of
    the atomic start function call for this compound statement.</p>
    """
    superclass = Statement
    idLabels = ReferenceListField("IdLabel")
    declarations = ReferenceListField("Declaration")
    statements = ReferenceListField("Statement")
    environment = ReferenceField("Environment", constructor_variable=False, visitable=False,
                                 deep_copy_mode=DEEP_COPY_MODE.ASSIGN_NULL)
    atomicVariableUniqueName = StringField(constructor_variable=False, optional=True)


class IfStmt(BasicASTNode):
    """
    <p>If statement. The <code>falseStatement</code> is optional.</p>
    """
    superclass = Statement
    condition = ReferenceField("Expression")
    trueStatement = ReferenceField("Statement")
    falseStatement = ReferenceField("Statement", optional=True)


class LabeledStmt(BasicASTNode):
    """
    <p>Labeled statement is a statement preceded by a label.</p>
    """
    superclass = Statement
    label = ReferenceField("Label")
    statement = ReferenceField("Statement", optional=True)


class ExpressionStmt(BasicASTNode):
    """
    <p>Expression statement.</p>
    """
    superclass = Statement
    expression = ReferenceField("Expression")


class ConditionalStmt(BasicASTNode):
    """
    <p>Base class for all conditional statements.</p>
    """
    superclass = Statement
    condition = ReferenceField("Expression")
    statement = ReferenceField("Statement")


class WhileStmt(BasicASTNode):
    """
    <p>While statement.</p>
    """
    superclass = ConditionalStmt


class DoWhileStmt(BasicASTNode):
    """
    <p>Do-while statement.</p>
    """
    superclass = ConditionalStmt


class SwitchStmt(BasicASTNode):
    """
    <p>Switch statement.</p>
    <p><code>firstLabel</code> points to the first label. The remaining labels are in
    {@link ConditionalStmt#statement} field.</p>
    """
    superclass = ConditionalStmt
    firstLabel = ReferenceField("Label", constructor_variable=False, visitable=False)


class ForStmt(BasicASTNode):
    """
    <p>For loop statement.</p>
    """
    superclass = Statement
    initExpression = ReferenceField("Expression", optional=True)
    conditionExpression = ReferenceField("Expression", optional=True)
    incrementExpression = ReferenceField("Expression", optional=True)
    statement = ReferenceField("Statement")


class BreakStmt(BasicASTNode):
    """
    <p>Break statement.</p>
    """
    superclass = Statement
    isAtomicSafe = BoolField(constructor_variable=False)


class ContinueStmt(BasicASTNode):
    """
    <p>Continue statement.</p>
    """
    superclass = Statement
    isAtomicSafe = BoolField(constructor_variable=False)


class ReturnStmt(BasicASTNode):
    """
    <p>Return statement. The <code>value</code> is optional.</p>
    """
    superclass = Statement
    value = ReferenceField("Expression", optional=True)
    isAtomicSafe = BoolField(constructor_variable=False)


class GotoStmt(BasicASTNode):
    """
    <p>Goto statement.</p>
    <code>toNonAtomicArea</code> is set to <code>true</code> during the semantic analysis
    if and only if the target label is not located inside the atomic statement. Otherwise,
    it is set to <code>false</code>.
    """
    superclass = Statement
    idLabel = ReferenceField("IdLabel")
    toNonAtomicArea = BoolField(constructor_variable=False)
    isAtomicSafe = BoolField(constructor_variable=False)


class ComputedGotoStmt(BasicASTNode):
    """
    <p>Goto statement. This is a GNU extension, which allows to jump to a label represented by an expression.</p>
    <p>See: https://gcc.gnu.org/onlinedocs/gcc/Labels-as-Values.html#Labels-as-Values</p>
    """
    superclass = Statement
    address = ReferenceField("Expression")


class EmptyStmt(BasicASTNode):
    """
    <p>Empty statement.</p>
    """
    superclass = Statement


#==============================================================================
#                                  Expressions
#==============================================================================

class ErrorExpr(BasicASTNode):
    """ Placeholder for erroneous expressions. """
    superclass = Expression


class Unary(BasicASTNode):
    """ Base class of unary expressions. """
    superclass = Expression
    argument = ReferenceField("Expression")


class Binary(BasicASTNode):
    """ Base class of binary expressions. """
    superclass = Expression
    leftArgument = ReferenceField("Expression")
    rightArgument = ReferenceField("Expression")


class Comma(BasicASTNode):
    """ A comma separated list of expressions. """
    superclass = Expression
    expressions = ReferenceListField("Expression")


class SizeofType(BasicASTNode):
    """ Calculates the number of bytes of storage the expression occupies. """
    superclass = Expression
    asttype = ReferenceField("AstType")


class Offsetof(BasicASTNode):
    """ """
    superclass = Expression
    typename = ReferenceField("AstType")
    fieldlist = ReferenceListField("FieldIdentifier")


class AlignofType(BasicASTNode):
    """
    Allows to inquire about how an object is aligned, or the minimum alignment usually required by a type.
    """
    superclass = Expression
    asttype = ReferenceField("AstType")


class LabelAddress(BasicASTNode):
    """
    <p>
    You can get the address of a label defined in the current function (or a containing function) with the unary
    operator ‘&&’. The value has type void *. This value is a constant and can be used wherever a constant of that type
    is valid. For example:

    <pre>
        void *ptr;
        ptr = &&foo;
    </pre>

    To use these values, you need to be able to jump to one. This is done with the computed goto statement, goto *exp;.
    For example,

    <pre>
        goto *ptr;
    </pre>
    </p>
    <p>gcc.gnu.org/onlinedocs/gcc/Labels-as-Values.html</p>
    """
    superclass = Expression
    idLabel = ReferenceField("IdLabel")


class Cast(BasicASTNode):
    superclass = Unary
    asttype = ReferenceField("AstType")


class CastList(BasicASTNode):
    superclass = Expression
    asttype = ReferenceField("AstType")
    initExpr = ReferenceField("Expression")


class Conditional(BasicASTNode):
    """
    Conditional expression. The middle operand in a conditional expression may be omitted. Then if the first operand
    is nonzero, its value is the value of the conditional expression.
    """
    superclass = Expression
    condition = ReferenceField("Expression")
    onTrueExp = ReferenceField("Expression", optional=True)
    onFalseExp = ReferenceField("Expression")


class Identifier(BasicASTNode):
    """
    <p><code>isGenericReference</code> is <code>true</code> after semantic analysis if and only if this identifier
    occurs inside a generic component definition and refers to one of its generic non-type parameters.</p>
    <p><code>uniqueName</code> is absent if and only if this identifier refers to a name of a command or event or
    appears inside a GCC attribute. If an error is detected during the semantic analysis, the name can be
    <code>null</code>.</p>
    """
    superclass = Expression
    mangleIndicator = MangleIndicator("uniqueName", "refsDeclInThisNescEntity", optional=True)
    name = StringField()
    isGenericReference = BoolField(constructor_variable=False)
    declaration = ReferenceField("ObjectDeclaration", constructor_variable=False, visitable=False,
                                 deep_copy_mode=DEEP_COPY_MODE.ASSIGN_REFERENCE_COPY)


class CompoundExpr(BasicASTNode):
    """
    <p>A compound statement enclosed in parentheses may appear as an expression in GNU C. This allows you to use loops,
    switches, and local variables within an expression.</p>
    <p>http://gcc.gnu.org/onlinedocs/gcc/Statement-Exprs.html</p>
    """
    superclass = Expression
    statement = ReferenceField("Statement")


class FunctionCall(BasicASTNode):
    """
    <p>Function call.</p>
    <p>If vaArgCall is present, this is actually a call to the pseudo-function __builtin_va_arg(arguments, vaArgCall)
    where vaArgCall is a type. In this case function is a dummy identifier.</p>
    <p>If <code>hasAtomicOrigin</code> is set to <code>true</code>, this AST node has been created as the result of
    atomic unfolding.</p>
    """
    superclass = Expression
    function = ReferenceField("Expression")
    arguments = ReferenceListField("Expression")
    vaArgCall = ReferenceField("AstType", constructor_variable=False)
    callKind = ReferenceField("NescCallKind", deep_copy_mode=DEEP_COPY_MODE.ASSIGN_REFERENCE_COPY)
    hasAtomicOrigin = BoolField(constructor_variable=False)


class ConstantFunctionCall(BasicASTNode):
    """
    <p>Call to a NesC compile-time constant function</p>
    <p>This node represents a call to one of NesC builtin, constant functions:</p>
    <ul>
        <li><code>unique</code></li>
        <li><code>uniqueN</code></li>
        <li><code>uniqueCount</code></li>
    </ul>
    <p>Identifier is the string that is the first parameter for a constant function.
    It is set in the process of folding constant functions calls.</p>
    """
    superclass = FunctionCall
    value = ReferenceField("Long", constructor_variable=False, deep_copy_mode=DEEP_COPY_MODE.ASSIGN_REFERENCE_COPY)
    identifier = StringField(constructor_variable=False)


class UniqueCall(BasicASTNode):
    """
    <p>Call to <code>unique</code> builtin, NesC constant function.</p>
    """
    superclass = ConstantFunctionCall
    uniqueIndicator = UniqueIndicator()


class UniqueNCall(BasicASTNode):
    """
    <p>Call to <code>uniqueN</code> builtin, NesC constant function.</p>
    """
    superclass = ConstantFunctionCall
    uniqueIndicator = UniqueIndicator()


class UniqueCountCall(BasicASTNode):
    """
    <p>Call to <code>uniqueCount</code> builtin, NesC constant function.</p>
    """
    superclass = ConstantFunctionCall
    uniqueIndicator = UniqueIndicator()


class ArrayRef(BasicASTNode):
    """
    <p>Array reference</p>
    <p>NOTICE: originally this node was extending BinaryExpression.</p>
    """
    superclass = Expression
    array = ReferenceField("Expression")
    index = ReferenceListField("Expression")


class FieldRef(BasicASTNode):
    superclass = Unary
    fieldName = StringField()
    declaration = ReferenceField("FieldDeclaration", constructor_variable=False, visitable=False,
                                 deep_copy_mode=DEEP_COPY_MODE.ASSIGN_REFERENCE_COPY)


class Dereference(BasicASTNode):
    superclass = Unary


class ExtensionExpr(BasicASTNode):
    superclass = Unary


class SizeofExpr(BasicASTNode):
    superclass = Unary


class AlignofExpr(BasicASTNode):
    superclass = Unary


class Realpart(BasicASTNode):
    superclass = Unary


class Imagpart(BasicASTNode):
    superclass = Unary


class AddressOf(BasicASTNode):
    superclass = Unary


class UnaryMinus(BasicASTNode):
    superclass = Unary


class UnaryPlus(BasicASTNode):
    superclass = Unary


class Conjugate(BasicASTNode):
    superclass = Unary


class Bitnot(BasicASTNode):
    superclass = Unary


class Not(BasicASTNode):
    superclass = Unary


class Increment(BasicASTNode):
    superclass = Unary


class Preincrement(BasicASTNode):
    superclass = Increment


class Predecrement(BasicASTNode):
    superclass = Increment


class Postincrement(BasicASTNode):
    superclass = Increment


class Postdecrement(BasicASTNode):
    superclass = Increment


class Plus(BasicASTNode):
    superclass = Binary


class Minus(BasicASTNode):
    superclass = Binary


class Times(BasicASTNode):
    superclass = Binary


class Divide(BasicASTNode):
    superclass = Binary


class Modulo(BasicASTNode):
    superclass = Binary


class Lshift(BasicASTNode):
    superclass = Binary


class Rshift(BasicASTNode):
    superclass = Binary


class Comparison(BasicASTNode):
    superclass = Binary


class Leq(BasicASTNode):
    superclass = Comparison


class Geq(BasicASTNode):
    superclass = Comparison


class Lt(BasicASTNode):
    superclass = Comparison


class Gt(BasicASTNode):
    superclass = Comparison


class Eq(BasicASTNode):
    superclass = Comparison


class Ne(BasicASTNode):
    superclass = Comparison


class Bitand(BasicASTNode):
    superclass = Binary


class Bitor(BasicASTNode):
    superclass = Binary


class Bitxor(BasicASTNode):
    superclass = Binary


class Andand(BasicASTNode):
    superclass = Binary


class Oror(BasicASTNode):
    superclass = Binary


class Assignment(BasicASTNode):
    superclass = Binary


class Assign(BasicASTNode):
    superclass = Assignment


class PlusAssign(BasicASTNode):
    superclass = Assignment


class MinusAssign(BasicASTNode):
    superclass = Assignment


class TimesAssign(BasicASTNode):
    superclass = Assignment


class DivideAssign(BasicASTNode):
    superclass = Assignment


class ModuloAssign(BasicASTNode):
    superclass = Assignment


class LshiftAssign(BasicASTNode):
    superclass = Assignment


class RshiftAssign(BasicASTNode):
    superclass = Assignment


class BitandAssign(BasicASTNode):
    superclass = Assignment


class BitorAssign(BasicASTNode):
    superclass = Assignment


class BitxorAssign(BasicASTNode):
    superclass = Assignment


class InitList(BasicASTNode):
    """
    <p>Initializer of list of elements.</p>
    <p>http://gcc.gnu.org/onlinedocs/gcc/Designated-Inits.html</p>

    <pre>
        int a[6] = { 0, 0, 15, 0, 29, 0 };
    </pre>
    """
    superclass = Expression
    arguments = ReferenceListField("Expression")


class InitSpecific(BasicASTNode):
    """
    <p>Initializer of specific elements.</p>
    <p>http://gcc.gnu.org/onlinedocs/gcc/Designated-Inits.html</p>

    <pre>
        int a[6] = { [4] = 29, [2] = 15 };
    </pre>
    """
    superclass = Expression
    designator = ReferenceListField("Designator")
    initExpr = ReferenceField("Expression")


class Designator(BasicASTNode):
    """ Base class for designated initializers. """
    superclass = Node


class DesignateField(BasicASTNode):
    """
    <p>In a structure initializer, one can specify the name of a field to initialize.</p>
    <p>http://gcc.gnu.org/onlinedocs/gcc/Designated-Inits.html</p>

    <p>
    For example, given the following structure:
    <pre>
        struct point { int x, y; };
    </pre>
    the following initialization is possible:
    <pre>
        struct point p = { .y = yvalue, .x = xvalue };
    </pre>
    </p>
    """
    superclass = Designator
    name = StringField()


class DesignateIndex(BasicASTNode):
    """
    <p>GNU extension allows to initialize a range of elements to the same value.</p>
    <p>http://gcc.gnu.org/onlinedocs/gcc/Designated-Inits.html</p>

    <pre>
    int widths[] = { [0 ... 9] = 1, [10 ... 99] = 2, [100] = 3 };
    </pre>
    """
    superclass = Designator
    first = ReferenceField("Expression")
    last = ReferenceField("Expression", optional=True)


#==============================================================================
#                                   Constants
#==============================================================================

class LexicalCst(BasicASTNode):
    """ A constant kept in unparsed form. """
    superclass = Expression
    string = StringField()


class IntegerCst(BasicASTNode):
    """
    <p>An integer constant.</p>
    <p>The value is present if and only if it belongs to the following set:</p>
    <pre>{ 0, &hellip;, 2<sup>64</sup> - 1 }</span>
    """
    superclass = LexicalCst
    value = ReferenceField("BigInteger", optional=True, deep_copy_mode=DEEP_COPY_MODE.ASSIGN_REFERENCE_COPY)
    kind = ReferenceField("IntegerCstKind", deep_copy_mode=DEEP_COPY_MODE.ASSIGN_REFERENCE_COPY)
    suffix = ReferenceField("IntegerCstSuffix", deep_copy_mode=DEEP_COPY_MODE.ASSIGN_REFERENCE_COPY)


class FloatingCst(BasicASTNode):
    """ A floating constant. """
    superclass = LexicalCst


class CharacterCst(BasicASTNode):
    """
    <p>A character constant.</p>
    <p>The value is absent if and only if it is specified incorrectly, e.g. when
    an invalid escape sequence is used.</p>
    """
    superclass = LexicalCst
    value = ReferenceField("Character", optional=True, deep_copy_mode=DEEP_COPY_MODE.ASSIGN_REFERENCE_COPY)


class StringCst(BasicASTNode):
    """ A single lexical string. """
    superclass = LexicalCst


class StringAst(BasicASTNode):
    """ A list of StringCst nodes forming a single string constant. """
    superclass = Expression
    strings = ReferenceListField("StringCst")


#==============================================================================
#                                     Labels
#==============================================================================

class IdLabel(BasicASTNode):
    superclass = Label
    id = StringField()
    isColonTerminated = BoolField(constructor_variable=False)
    declaration = ReferenceField("LabelDeclaration", constructor_variable=False, visitable=False,
                                 deep_copy_mode=DEEP_COPY_MODE.ASSIGN_REFERENCE_COPY)


class CaseLabel(BasicASTNode):
    """
    <p>C extensions allows to use in switch statement case ranges:</p>
    <pre>
        case low ... high:
    </pre>

    <p>NOTICE: Be careful: Write spaces around the ..., for otherwise it may be parsed wrong when you use it with
    integer values.</p>
    """
    superclass = Label
    low = ReferenceField("Expression")
    high = ReferenceField("Expression", optional=True)


class DefaultLabel(BasicASTNode):
    """ Default label is switch-case construct. """
    superclass = Label


#==============================================================================
#                                 Miscellaneous
#==============================================================================

class Word(BasicASTNode):
    """
    <p>A convenient class for representing identifiers in the source code. It additionally contains location fields.<p>
    """
    superclass = Node
    name = StringField()


# TODO: description
class AsmOperand(BasicASTNode):
    superclass = Node
    word1 = ReferenceField("Word", optional=True)
    string = ReferenceField("StringAst")
    arg1 = ReferenceField("Expression")


class FieldIdentifier(BasicASTNode):
    """
    <p>This AST node represents an identifier that designates a field in an
    offsetof expression:</p>

    <pre>
        union u { char c; int n; double d; };
        struct s { int n; char c; union u un; float f; };
        &#x22ee;
        offsetof(struct s, un.c);
    </pre>

    <p><code>un</code> and <code>c</code> from the offsetof expression are
    represented by <code>FieldIdentifier</code> AST nodes.</p>
    """
    superclass = Node
    name = StringField()
    declaration = ReferenceField("FieldDeclaration", constructor_variable=False, visitable=False,
                                 deep_copy_mode=DEEP_COPY_MODE.ASSIGN_REFERENCE_COPY)


#==============================================================================
#                                nesc extensions
#==============================================================================

#==============================================================================
#                          The different kinds of files
#==============================================================================

class NescDecl(BasicASTNode):
    """ Base class for nesc component or interface declaration. """
    superclass = Declaration
    name = ReferenceField("Word")
    attributes = ReferenceListField("Attribute")


class Interface(BasicASTNode):
    """ Interface definition. """
    superclass = NescDecl
    parameters = ReferenceListField("Declaration", optional=True)
    declarations = ReferenceListField("Declaration")
    declaration = ReferenceField("InterfaceDeclaration", constructor_variable=False, visitable=False,
                                 deep_copy_mode=DEEP_COPY_MODE.ASSIGN_NULL)
    parameterEnvironment = ReferenceField("Environment", constructor_variable=False, visitable=False,
                                          deep_copy_mode=DEEP_COPY_MODE.ASSIGN_NULL)
    declarationEnvironment = ReferenceField("Environment", constructor_variable=False, visitable=False,
                                            deep_copy_mode=DEEP_COPY_MODE.ASSIGN_NULL)


class Component(BasicASTNode):
    """
    <p>Base class for nesc component.</p>
    <p><code>instantiationChain</code> is the sequence of components starting
    with a non-generic configuration that specifies the origin and cause of
    instantiation of this component. The last element in the chain represents
    this component. The object is absent if this component is not the result
    of instantiation of another component.</p>
    """
    superclass = NescDecl
    isAbstract = BoolField()
    parameters = ReferenceListField("Declaration", optional=True)
    declarations = ReferenceListField("Declaration")
    implementation = ReferenceField("Implementation")
    parameterEnvironment = ReferenceField("Environment", constructor_variable=False, visitable=False,
                                          deep_copy_mode=DEEP_COPY_MODE.ASSIGN_NULL)
    specificationEnvironment = ReferenceField("Environment", constructor_variable=False, visitable=False,
                                              deep_copy_mode=DEEP_COPY_MODE.ASSIGN_NULL)
    instantiationChain = ReferenceField("ImmutableList<InstantiationOrigin>", constructor_variable=False,
                                        optional=True, deep_copy_mode=DEEP_COPY_MODE.ASSIGN_NULL)


class Configuration(BasicASTNode):
    superclass = Component
    declaration = ReferenceField("ConfigurationDeclaration", constructor_variable=False, visitable=False,
                                 deep_copy_mode=DEEP_COPY_MODE.ASSIGN_NULL)


class Module(BasicASTNode):
    """
    Module table contains information about commands and events that this
    module must or can implement. The field is not <code>null</code> after
    parsing and analyzing the specification of this module.
    """
    superclass = Component
    declaration = ReferenceField("ModuleDeclaration", constructor_variable=False, visitable=False,
                                 deep_copy_mode=DEEP_COPY_MODE.ASSIGN_NULL)
    moduleTable = ReferenceField("ModuleTable", constructor_variable=False, visitable=False,
                                 deep_copy_mode=DEEP_COPY_MODE.ASSIGN_EXTERNAL_DEEP_COPY)


class BinaryComponent(BasicASTNode):
    superclass = Component


class Implementation(BasicASTNode):
    superclass = Node
    environment = ReferenceField("Environment", constructor_variable=False, visitable=False,
                                 deep_copy_mode=DEEP_COPY_MODE.ASSIGN_NULL)
    #cdecl = ReferenceField("NescDeclaration", constructor_variable=False, visitable=False)


class ConfigurationImpl(BasicASTNode):
    superclass = Implementation
    declarations = ReferenceListField("Declaration")


class ModuleImpl(BasicASTNode):
    superclass = Implementation
    declarations = ReferenceListField("Declaration")


class BinaryComponentImpl(BasicASTNode):
    superclass = Implementation


class ComponentsUses(BasicASTNode):
    """
    <p>This node was not present in original compiler.</p>

    <pre>
        configuration NullAppC{}
            implementation {
            components MainC, NullC; # <- components uses
            MainC.Boot <- NullC;
        }
    </p>
    """
    superclass = Declaration
    components = ReferenceListField("ComponentRef")


#==============================================================================
#                           Component definition types
#==============================================================================

class RpInterface(BasicASTNode):
    superclass = Declaration
    declarations = ReferenceListField("Declaration")


class RequiresInterface(BasicASTNode):
    """ List of required interfaces by component. """
    superclass = RpInterface


class ProvidesInterface(BasicASTNode):
    """ List of interfaces provided by component. """
    superclass = RpInterface


class InterfaceRef(BasicASTNode):
    """
    <p>Interface reference in component specification.</p>
    <p>'uses'/'provides' 'interface' NAME '<'ARGUMENTS'>' '['GENERIC_PARAMETERS']' 'as' ALIAS ATTRIBUTES;</p>

    <pre>
        configuration All {
            provides interface A as ProvidedA1;
            provides interface A as ProvidedA2;
            provides interface A as ProvidedA3;
            uses interface A as UsedA1;
        }
    </pre>
    """
    superclass = Declaration
    name = ReferenceField("Word")
    arguments = ReferenceListField("Expression", optional=True)
    alias = ReferenceField("Word", constructor_variable=False, optional=True)
    genericParameters = ReferenceListField("Declaration", constructor_variable=False, optional=True)
    attributes = ReferenceListField("Attribute", constructor_variable=False)
    declaration = ReferenceField("InterfaceRefDeclaration", constructor_variable=False, visitable=False,
                                 deep_copy_mode=DEEP_COPY_MODE.ASSIGN_REFERENCE_COPY)


class ComponentRef(BasicASTNode):
    superclass = Declaration
    name = ReferenceField("Word")
    alias = ReferenceField("Word", constructor_variable=False, optional=True)
    isAbstract = BoolField()
    arguments = ReferenceListField("Expression")
    declaration = ReferenceField("ComponentRefDeclaration", constructor_variable=False, visitable=False,
                                 deep_copy_mode=DEEP_COPY_MODE.ASSIGN_REFERENCE_COPY)


class Connection(BasicASTNode):
    """
    <p>Wiring statement connecting two endpoints.</p>
    <p>Call direction indicates provided interfaces and the implementation of bare
    commands and events. If an error is detected during the semantic analysis, the
    value of call direction can be <code>null</code>.</p>
    @see pl.edu.mimuw.nesc.ast.CallDirection CallDirection
    """
    superclass = Declaration
    endPoint1 = ReferenceField("EndPoint")
    endPoint2 = ReferenceField("EndPoint")
    callDirection = ReferenceField("CallDirection", deep_copy_mode=DEEP_COPY_MODE.ASSIGN_REFERENCE_COPY,
                                   constructor_variable=False)


class RpConnection(BasicASTNode):
    """ Link wire. """
    superclass = Connection


class EqConnection(BasicASTNode):
    """ Equate wire. """
    superclass = Connection


class EndPoint(BasicASTNode):
    """
    <p>Implicit identifier is present after semantic analysis if and only if this endpoint denotes a component
    and is an element of a correct implicit connection. If so, it is the name of the specification element from
    the component referred by the only identifier in <code>ids</code> that forms the connection. If an error is
    detected during the semantic analysis, the identifier can be <code>null</code>.</p>
    """
    superclass = Node
    ids = ReferenceListField("ParameterisedIdentifier")
    implicitIdentifier = StringField(optional=True, constructor_variable=False)


class ParameterisedIdentifier(BasicASTNode):
    """
    Endpoint can be parameterised.

    <pre>
        Receive = ActiveMessageC.Receive[amId];
    </pre>
    """
    superclass = Node
    name = ReferenceField("Word")
    arguments = ReferenceListField("Expression")


#==============================================================================
#                  Types for extensions to the regular C syntax
#==============================================================================

class GenericCall(BasicASTNode):
    """
    <p>Parameterised interface function call.</p>
    <p>name: name or alias of interface</p>

    <pre>
        err = call AMSend.send[amId](dest, msg, len);
    </pre>
    """
    superclass = Expression
    name = ReferenceField("Expression")
    arguments = ReferenceListField("Expression")


class InterfaceRefDeclarator(BasicASTNode):
    """
    <p>Declarator for interface command/event.</p>
    <p>name: name or alias of interface</p>

    <pre>
        command error_t Send.send[uint8_t clientId](message_t* msg, uint8_t len) { ...
    </pre>
    """
    superclass = NestedDeclarator
    name = ReferenceField("Word")


class InterfaceDeref(BasicASTNode):
    """
    Invocation of interface command.

    <pre>
        am_id_t amId = call AMPacket.type(msg);
    </pre>
    """
    superclass = Unary
    methodName = ReferenceField("Word")
    # FIXME: does it need declaration reference?
    #declaration = ReferenceField("ObjectDeclaration", constructor_variable=False, visitable=False)


class ComponentDeref(BasicASTNode):
    """
    Reference to component's field.

    <pre>
        module M {
            enum { one = 1 };
            ...
        } ...

        configuration C {}
        implementation {
            components M as First;
            enum { two = First.one * 2 };
            ...
        }
    </pre>
    """
    superclass = Unary
    fieldName = ReferenceField("Word")
    # FIXME: does it need declaration reference?
    #declaration = ReferenceField("ObjectDeclaration", constructor_variable=False, visitable=False)


class ComponentTyperef(BasicASTNode):
    """
    Reference to a typedef in component.

    <pre>
        module M {
            typedef int my_t;
            ...
        } ...

        configuration C {}
        implementation {
            components M as First;
            typedef First.my_t conf_C_t;
            ...
        }
    </pre>
    """
    superclass = Typename
    typeName = StringField()


class AtomicStmt(BasicASTNode):
    """
    <code>definedLabelsNames</code> is a set with names of all labels that are defined inside
    this atomic statement. A defined label is a label occurrence ended with a colon. The set
    is absent if this is a nested atomic statement.
    """
    superclass = Statement
    statement = ReferenceField("Statement")
    declaredLabelsNames = ReferenceField("Set<String>", deep_copy_mode=DEEP_COPY_MODE.ASSIGN_REFERENCE_COPY,
                                         optional=True)


class NxStructRef(BasicASTNode):
    superclass = StructRef


class NxUnionRef(BasicASTNode):
    superclass = UnionRef


class NescAttribute(BasicASTNode):
    """ NesC attribute decorated with @. """
    superclass = Attribute
    value = ReferenceField("Expression")
    declaration = ReferenceField("AttributeDeclaration", constructor_variable=False, visitable=False,
                                 deep_copy_mode=DEEP_COPY_MODE.ASSIGN_REFERENCE_COPY)


class TargetAttribute(BasicASTNode):
    """ A target-specific extension represented internally as a gcc-style attribute. """
    superclass = GccAttribute


#==============================================================================
#                      Types for the polymorphic extensions
#==============================================================================

class TypeParmDecl(BasicASTNode):
    """
    Type parameter declaration in generic interface declaration.

    <pre>
        interface Queue<t> { ... }
        interface Timer<precision_tag> { ... }
    </pre>
    """
    superclass = Declaration
    mangleIndicator = MangleIndicator("uniqueName", "isNestedInNescEntity")
    name = StringField()
    attributes = ReferenceListField("Attribute")
    declaration = ReferenceField("TypenameDeclaration", constructor_variable=False, visitable=False,
                                 deep_copy_mode=DEEP_COPY_MODE.ASSIGN_REFERENCE_COPY)


class TypeArgument(BasicASTNode):
    """
    Type parameter in generic components. For example:

    <pre>
        components new QueueC(_srf_queue_entry_t*, QUEUE_SIZE) as SendQueue;
    </pre>
    """
    superclass = Expression
    asttype = ReferenceField("AstType")

#==============================================================================
#==============================================================================
if __name__ == "__main__":
    generate_code(DST_LANGUAGE.JAVA, "pl/edu/mimuw/nesc/ast/gen")
