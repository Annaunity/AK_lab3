; Запросить имя пользователя (на одной строке) и поприветствовать его
; Данный пример - смесь примеров hello и cat.

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
_break:

_cat:       ld IN
            sub const10
            jz _break_cat
            add const10
            st OUT
            jmp _cat
_break_cat: 

            ld const33
            st OUT
            hlt

message:    string "Hello, "
ptr:        data message
limit:      data 0
const1:     data 1
const10:    data 10 ; ascii \n
const33:    data 33 ; ascii !
