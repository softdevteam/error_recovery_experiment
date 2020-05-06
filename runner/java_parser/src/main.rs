use std::env;
use std::fs::read_to_string;

use lrlex::lrlex_mod;
use lrpar::lrpar_mod;

use lrpar::{NonStreamingLexer, ParseRepair, LexParseError, Lexer};

// Using `lrlex_mod!` brings the lexer for `calc.l` into scope.
lrlex_mod!("java7.l");
// Using `lrpar_mod!` brings the parser for `calc.y` into scope.
lrpar_mod!("java7.y");

fn main() {
    // We need to get a `LexerDef` for the `calc` language in order that we can lex input.
    let lexerdef = java7_l::lexerdef();
    let d = read_to_string(env::args().nth(1).unwrap()).unwrap();
    let lexer = lexerdef.lexer(&d);
    let lexemes = lexer.iter().collect::<Vec<_>>();
    println!("Lexeme count: {}", lexemes.len());
    let mut lexer = lexerdef.lexer(&d);
    let mut skipped = 0;

    let errs = java7_y::parse(&mut lexer);
    if errs.is_empty() {
        println!("Parsed successfully");
    } else {
        let mut completed = true;
        for e in errs {
            match e {
                LexParseError::LexError(e) => {
                    let ((line, col), _) = lexer.line_col(e.span());
                    println!("Lexing error at line {} column {:?}", line, col);
                    completed = false;
                }
                LexParseError::ParseError(e) => {
                    let ((line, col), _) = lexer.line_col(e.lexeme().span());
                    println!("Error at line {} col {}", line, col);
                    if e.repairs().is_empty() {
                        completed = false;
                    } else {
                        for r in &e.repairs()[0] {
                            if let ParseRepair::Delete(_) = *r {
                                skipped += 1;
                            }
                        }
                    }
                }
            }
        }
        if !completed {
            println!("Parsing did not complete");
        }
    }
    println!("Input skipped: {}", skipped);
}

