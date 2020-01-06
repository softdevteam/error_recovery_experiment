extern crate cfgrammar;
extern crate lrlex;
extern crate lrpar;

use cfgrammar::yacc::{YaccKind, YaccOriginalActionKind};
use lrlex::LexerBuilder;
use lrpar::{
    CTParserBuilder, RecoveryKind,
};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let lex_rule_ids_map = CTParserBuilder::<u16>::new_with_storaget()
        .yacckind(YaccKind::Original(YaccOriginalActionKind::NoAction))
        .recoverer(RecoveryKind::CPCTPlus)
        .process_file_in_src("java7.y")?;
    LexerBuilder::new()
        .rule_ids_map(lex_rule_ids_map)
        .process_file_in_src("java7.l")?;
    Ok(())
}
