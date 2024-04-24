grammar mu;
music
    : nls (group ';' nlp)* group final nls EOF
    ;
final
    : ':' nlp (num spp)* num
    | '|'
    ;
group
    : mod spp mtr spp bmp nlp (passage ',' nlp)* passage
    ;
mod
    : alpha accid octav
    ;
mtr
    : num '/' num
    ;
bmp
    : num
    ;
passage
    : (measure nls)* measure
    ;
measure
    : (element sps)+ '|'
    ;
element
    : note time
    | '<' (element sps)* element '>'
    | rat (element sps)* element '!'
    ;
rat
    : '[' num ':' num ']'
    ;
note
    : solfa accid octav
    | rest
    | tie
    ;
time
    : (sps '-')*
    | '/'* (sps '.')*
    ;
accid
    : '='?
    | 'b'*
    | '#'*
    ;
octav
    : '^'*
    | 'v'*
    ;
num
    : ('1' | '2' | '3' | '4' | '5' | '6' | '7' | '8' | '9') ('0' | '1' | '2' | '3' | '4' | '5' | '6' | '7' | '8' | '9')*
    ;
alpha
    : 'A' | 'B' | 'C' | 'D' | 'E' | 'F' | 'G'
    ;
solfa
    : '1' | '2' | '3' | '4' | '5' | '6' | '7'
    ;
rest
    : '0'
    ;
tie
    : '*'
    ;
spp
    : ' '+
    ;
sps
    : ' '*
    ;
nlp
    : ' '* (('\n' | '\r') ' '*)+
    ;
nls
    : ' '* (('\n' | '\r') ' '*)*
    ;
