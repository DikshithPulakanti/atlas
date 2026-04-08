/// AtlasQL lexer — tokenizes query strings into a stream of tokens.
///
/// Pipeline stage 1: raw query string → token stream.
/// Uses the `logos` crate for fast, zero-copy tokenization of AtlasQL keywords,
/// identifiers, literals, operators, and punctuation.
pub struct Lexer;
