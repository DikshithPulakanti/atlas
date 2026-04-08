/// AtlasQL parser — builds an AST from the token stream.
///
/// Pipeline stage 2: token stream → AST.
/// Uses recursive descent for statements and Pratt parsing for expressions
/// to correctly handle operator precedence and associativity.
pub struct Parser;
