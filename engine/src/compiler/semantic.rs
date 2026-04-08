/// Semantic analyzer — validates the AST against source schemas.
///
/// Pipeline stage 3: AST → validated AST.
/// Resolves column references against the schema catalog, checks type
/// compatibility across cross-source joins, and validates AI operator
/// arguments. Reports errors with source locations.
pub struct SemanticAnalyzer;
