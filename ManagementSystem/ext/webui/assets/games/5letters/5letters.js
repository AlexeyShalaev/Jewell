class LettersGame {
    #field
    #rows = 6
    #cols = 5
    #row
    #col
    #code
    #user_id

    constructor(user_id, code, field = 'game_field') {
        this.#field = document.getElementById(field);
        this.#row = 0;
        this.#col = 0;
        this.#code = code
        this.#user_id = user_id
        this.create_table();
    }

    keyboard_click(key) {
        if (key === 'Ввод') {
            if (this.#col === this.#cols) {
                let word = "";
                for (let col = 0; col < this.#cols; ++col) {
                    word += document.getElementById(`${this.#row}_${col}`).innerText;
                }
                this.#check_word(word);
            } else {
                $.NotificationApp.send("5БУКВ", "Слишком короткое слово", "top-center", "#FF5B5B", "info");
            }
        } else if (key.length === 0) {
            if (this.#col !== 0) {
                --this.#col;
                document.getElementById(`${this.#row}_${this.#col}`).classList.remove('selected');
                document.getElementById(`${this.#row}_${this.#col}`).setAttribute('data-animation', "none");
                document.getElementById(`${this.#row}_${this.#col}`).innerText = "";
            }
        } else {
            if (this.#col !== this.#cols) {
                document.getElementById(`${this.#row}_${this.#col}`).classList.add('selected');
                document.getElementById(`${this.#row}_${this.#col}`).setAttribute('data-animation', "pop");
                document.getElementById(`${this.#row}_${this.#col}`).innerText = key;
                ++this.#col;
            }
        }
    }

    #check_word(word) {
        $.ajax({
            type: 'POST',
            url: '/games/5letters/check',
            data: {
                "word": word, "code": this.#code, "user_id": this.#user_id
            },
            success: function (result) {
                check_result(JSON.parse(result), word);
            }
        });
    }

    async check_result(res, word) {
        if (res.status === 'win') {
            for (let i in word) {
                document.getElementById(`${this.#row}_${i}`).classList.add(`bg-success`);
            }
            let keys = document.getElementsByClassName("Game-keyboard-button");
            for (let key of keys) {
                key.onclick = null;
                key.classList.add(`bg-success-lighten`);
            }
            Swal.fire({
                title: '<strong>Победа</strong>',
                icon: 'success',
                html: `<div>Вы заработали:</div><br><strong>${res.extra}</strong>`,
                showCloseButton: true,
                focusConfirm: false,
                confirmButtonText: 'Начать заново?',
            }).then((result) => {
                if (result.isConfirmed) {
                    location.reload();
                }
            })
        } else if (res.status === 'incorrect') {
            const extra = res.extra;
            for (let i in word) {
                const r = extra[i];
                let color = '';
                let del_onclick = false;
                if (r === '-') {
                    del_onclick = true;
                    color = 'secondary';
                } else if (r === '+') {
                    color = 'success';
                } else {
                    color = 'warning';
                }
                let keys = document.getElementsByClassName("Game-keyboard-button");
                for (let key of keys) {
                    if (key.innerText.toUpperCase() === word[i]) {
                        //if (del_onclick) key.onclick = null;
                        key.classList.add(`bg-${color}-lighten`);
                        break;
                    }
                }
                document.getElementById(`${this.#row}_${i}`).classList.add(`bg-${color}`);
                document.getElementById(`${this.#row}_${i}`).classList.remove('selected');
                document.getElementById(`${this.#row}_${i}`).setAttribute('data-animation', "flip-in");
                await sleep(350);
                document.getElementById(`${this.#row}_${i}`).setAttribute('data-animation', "none");
            }
            ++this.#row;
            this.#col = 0;
        } else {
            $.NotificationApp.send("5БУКВ", "Слова нет в нашем словаре", "top-center", "#FF5B5B", "info");
        }
        if (this.#row === this.#rows) {
            let keys = document.getElementsByClassName("Game-keyboard-button");
            for (let key of keys) {
                key.onclick = null;
                key.classList.add(`bg-danger-lighten`);
            }
            $.ajax({
                type: 'POST',
                url: '/games/5letters/decode',
                data: {
                    "code": this.#code, "user_id": this.#user_id
                },
                success: function (result) {
                    Swal.fire({
                        title: '<strong>Проигрыш</strong>',
                        icon: 'info',
                        html: `<div>Загаданное слово:</div><br><strong>${JSON.parse(result).riddle}</strong>`,
                        showCloseButton: true,
                        focusConfirm: false,
                        confirmButtonText: 'Начать заново?',
                    }).then((result) => {
                        if (result.isConfirmed) {
                            location.reload();
                        }
                    })
                }
            });
        }
    }

    create_table() {
        this.#field.innerHTML = ""
        for (let row = 0; row < this.#rows; ++row) {
            let document_row = document.createElement("div");
            document_row.setAttribute('class', 'Row');
            for (let col = 0; col < this.#cols; ++col) {
                let document_col = document.createElement("div");
                document_col.setAttribute('class', 'Row-letter');
                document_col.setAttribute('data-animation', 'none');
                document_col.setAttribute('id', `${row}_${col}`);
                document_row.appendChild(document_col);
            }
            this.#field.appendChild(document_row);
        }
    }
}