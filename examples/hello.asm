            ; вычисляем максимальный адрес
            ld ptr
            add message
            st limit
            
_loop:      ; если указатель вышел за пределы строки, выходим из цикла
            ld ptr
            sub limit
            jns _break

            ; инкрементируем адрес
            ld ptr
            add const1
            st ptr

            ; выводим символ
            ldi ptr
            st OUT

            jmp _loop

_break:     hlt

message:    string "Hello, World!"
ptr:        data message
limit:      data 0
const1:     data 1
