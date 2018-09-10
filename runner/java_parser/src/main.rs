use std::env;
use std::fs::read_to_string;

#[macro_use] extern crate lrlex;
#[macro_use] extern crate lrpar;

use lrpar::ParseRepair;

// Using `lrlex_mod!` brings the lexer for `calc.l` into scope.
lrlex_mod!(java7_l);
// Using `lrpar_mod!` brings the lexer for `calc.l` into scope.
lrpar_mod!(java7_y);

fn main() {
    // We need to get a `LexerDef` for the `calc` language in order that we can lex input.
    let lexerdef = java7_l::lexerdef();
    let d = read_to_string(env::args().nth(1).unwrap()).unwrap();
    let lexer = lexerdef.lexer(&d);
    let lexemes = lexer.lexemes().unwrap();
    println!("Lexeme count: {}", lexemes.len());
    let mut skipped = 0;
    match java7_y::parse(&lexemes) {
        Ok(_) => println!("Parsed successfully"),
        Err((pt, errs)) => {
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

