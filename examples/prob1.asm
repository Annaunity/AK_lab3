            ; алгоритм: три цикла, первый суммирует числа кратные 3, второй - 5,
            ; а третий вычитает числа, кратные 15, которые были посчитаны дважды
            
            ; первый цикл: считаем от 0 до N с шагом 3

            ; ACC = 0
            clr
_loop1:     ; ACC += 3
            add const3

            ; если ACC >= N, выходим из цикла
            st tmp
            sub N
            jns _break1
            ld tmp

            ; sum += ACC
            st tmp
            ld sum
            add tmp
            st sum
            ld tmp

            jmp _loop1
_break1:

            ; второй цикл - аналогичен первому, но считаем с шагом 5
            clr
_loop2:     add const5
            st tmp
            sub N
            jns _break2
            ld tmp
            st tmp
            ld sum
            add tmp
            st sum
            ld tmp
            jmp _loop2
_break2:

            ; третий цикл, считаем с шагом 15, теперь вычитаем из суммы
            clr
_loop3:     add const15
            st tmp
            sub N
            jns _break3
            ld tmp
            st tmp
            ld sum
            sub tmp
            st sum
            ld tmp
            jmp _loop3
_break3:     

            ; далее идет реализация вывода числа в десятичной системе счисления
            ; поддерживается до 6 цифр
            ; алгоритм: для k-ой цифры, в цикле вычитаем из числа 10^k пока число не станет отрицательным

            ; выводим число 100000
            clr
            st tmp
_out1:      ld sum
            sub const100000
            js _out1_br
            st sum
            ld tmp
            add const1
            st tmp
            jmp _out1
_out1_br:   ld tmp
            add const48  ; 48 - символ '0' в ascii
            st OUT

            ; выводим число 10000
            clr
            st tmp
_out2:      ld sum
            sub const10000
            js _out2_br
            st sum
            ld tmp
            add const1
            st tmp
            jmp _out2
_out2_br:   ld tmp
            add const48
            st OUT

            ; выводим число 1000
            clr
            st tmp
_out3:      ld sum
            sub const1000
            js _out3_br
            st sum
            ld tmp
            add const1
            st tmp
            jmp _out3
_out3_br:   ld tmp
            add const48
            st OUT

            ; выводим число 100
            clr
            st tmp
_out4:      ld sum
            sub const100
            js _out4_br
            st sum
            ld tmp
            add const1
            st tmp
            jmp _out4
_out4_br:   ld tmp
            add const48
            st OUT

            ; выводим число 10
            clr
            st tmp
_out5:      ld sum
            sub const10
            js _out5_br
            st sum
            ld tmp
            add const1
            st tmp
            jmp _out5
_out5_br:   ld tmp
            add const48
            st OUT

            ; выводим число 1
            clr
            st tmp
_out6:      ld sum
            sub const1
            js _out6_br
            st sum
            ld tmp
            add const1
            st tmp
            jmp _out6
_out6_br:   ld tmp
            add const48
            st OUT

            hlt

N:          data 1000
tmp:        data 0
const1:     data 1
const3:     data 3
const5:     data 5
const15:    data 15
const10:    data 10
const48:    data 48
const100:   data 100
const1000:  data 1000
const10000: data 10000
const100000:data 100000
sum:        data 0
