use std::env;
use std::fs::read_to_string;

#[macro_use] extern crate lrlex;
#[macro_use] extern crate lrpar;

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
    match java7_y::parse(&lexemes) {
        Ok(_) => println!("Parsed successfully"),
        Err((pt, errs)) => {
            println!("Errors during parse");
            if pt.is_none() {
                println!("No repairs found.");
            } else {
                for e in errs {
                    let (line, col) = lexer.line_and_col(e.lexeme()).unwrap();
                    if e.repairs().is_empty() {
                        println!("Error at line {} col {}. No repairs found.", line, col);
                        continue;
                    }
                    println!("Error at line {} col {}. Repairs found.", line, col);
                }
            }
        }
    }
}

