use std::env;
use std::fs::read_to_string;

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
    let mut skipped = 0;
    match java7_y::parse(&mut lexer) {
        Ok(_) => println!("Parsed successfully"),
        Err(LexParseError::LexError(e)) => println!("Lexing error at column {:?}", e.idx),
        Err(LexParseError::ParseError(pt, errs)) => {
            for e in &errs {
                let (line, col) = lexer.line_and_col(e.lexeme()).unwrap();
                println!("Error at line {} col {}", line, col);
                if !e.repairs().is_empty() {
                    for r in &e.repairs()[0] {
                        if let ParseRepair::Delete = *r {
                            skipped += 1;
                        }
                    }
                }
            }
            if pt.is_none() {
                println!("Parsing did not complete");
            }
        }
    }
    println!("Input skipped: {}", skipped);
}

