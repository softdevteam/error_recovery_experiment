use std::env;
use std::fs::read_to_string;

extern crate cfgrammar;
#[macro_use] extern crate lrlex;
#[macro_use] extern crate lrpar;

use lrpar::{ParseRepair, LexParseError, Lexer};

// Using `lrlex_mod!` brings the lexer for `calc.l` into scope.
lrlex_mod!(java7_l);
// Using `lrpar_mod!` brings the lexer for `calc.l` into scope.
lrpar_mod!(java7_y);

fn main() {
    // We need to get a `LexerDef` for the `calc` language in order that we can lex input.
    let lexerdef = java7_l::lexerdef();
    let d = read_to_string(env::args().nth(1).unwrap()).unwrap();
    let mut lexer = lexerdef.lexer(&d);
    let lexemes = lexer.all_lexemes().unwrap();
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
                    println!("Lexing error at column {:?}", e.idx);
                    completed = false;
                }
                LexParseError::ParseError(e) => {
                    let (line, col) = lexer.offset_line_col(e.lexeme().start());
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

