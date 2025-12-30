//---- Intended for Apple Silicon ----//

.text
        .global _sign_asm
_sign_asm:

        //sign(x) = (x >>_{signed} 63) | (-x >>_{unsigned} 63)
        mov x1, x0
        neg x1, x1
        lsr x1, x1, #63
        asr x0, x0, #63
        orr x0, x0, x1
        
        ret