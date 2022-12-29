class JewellNet {
    #div_id;
    #network;
    #nodes;
    #edges;
    #startVertex = null;
    #finishVertex = null;
    contextMenuVertex;

    constructor(div_id, nodes, edges) {
        this.#div_id = div_id;
        this.#nodes = nodes;
        this.#edges = edges;
        this.#draw();
    }

    #draw() {
        try {
            const container = document.getElementById(this.#div_id);
            const data = {
                nodes: this.#nodes,
                edges: this.#edges,
            };
            const options = {
                nodes: {
                    borderWidth: 6,
                    size: 30,
                    color: {
                        border: "#222222",
                        background: "#666666",
                    },
                    font: {color: "#8F75DA",},
                },
                edges: {
                    color: "lightgray",
                    width: 5,
                    physics: false
                },
            };
            this.#network = new vis.Network(container, data, options);
            this.#network.on("oncontext", function (params) {
                const index = this.getNodeAt(params.pointer.DOM);
                if (index !== undefined) {
                    jewellNet.contextMenuVertex = index;
                    showMenu(params.event);
                }
            });

            this.#network.on("hold", function (params) {
                const index = this.getNodeAt(params.pointer.DOM);
                if (index !== undefined) {
                    jewellNet.contextMenuVertex = index;
                    showMenu(params.event);
                }
            });

            document.addEventListener(
                "click",
                (e) => {
                    contextMenu.style.visibility = "hidden";
                },
                {passive: false}
            );
        } catch (e) {
            console.log(e);
        }
    }

    whoIsThis() {
        let link = location.href.toString();
        link = link.substring(0, link.indexOf("relations"));
        window.open(link + "profile/" + this.contextMenuVertex);
    }

    setStartVertex(v = this.contextMenuVertex) {
        if (this.#startVertex === v) return;
        if (this.#finishVertex === v) this.#finishVertex = null;
        this.#startVertex = v;
        for (let i in this.#nodes) {
            if (this.#nodes[i].id === v) {
                this.#nodes[i]["color"] = {border: 'lime'};
                this.#nodes[i]["label"] = 'Отсюда';
            } else {
                if (this.#nodes[i].id !== this.#finishVertex) {
                    this.#nodes[i]["color"] = null;
                    this.#nodes[i]["label"] = null;
                }
            }
        }
        if (this.#finishVertex != null && this.#finishVertex !== this.#startVertex) {
            this.#get_way();
        } else {
            for (let i in this.#edges) {
                if (this.#edges[i]["color"] !== undefined) {
                    this.#edges[i]["color"] = null;
                }
            }
            this.#draw();
        }
    }

    setFinishVertex(v = this.contextMenuVertex) {
        if (this.#finishVertex === v) return;
        if (this.#startVertex === v) this.#startVertex = null;
        this.#finishVertex = v;
        for (let i in this.#nodes) {
            if (this.#nodes[i].id === v) {
                this.#nodes[i]["color"] = {border: '#FFA500'};
                this.#nodes[i]["label"] = 'Сюда';
            } else {
                if (this.#nodes[i].id !== this.#startVertex) {
                    this.#nodes[i]["color"] = null;
                    this.#nodes[i]["label"] = null;
                }
            }
        }
        if (this.#startVertex != null && this.#finishVertex !== this.#startVertex) {
            this.#get_way();
        } else {
            for (let i in this.#edges) {
                if (this.#edges[i]["color"] !== undefined) {
                    this.#edges[i]["color"] = null;
                }
            }
            this.#draw();
        }
    }

    #get_way() {
        $.ajax({
            type: 'POST',
            url: '/api/networking/way',
            data:
                {
                    "startVertex": this.#startVertex,
                    "finishVertex": this.#finishVertex,
                },
            success: function (result) {
                const res = JSON.parse(result);
                if (res.success === true && res.way.length>0) {
                    jewellNet.show_way(res.way);
                } else {
                    $.NotificationApp.send("Связи", "Не удалось вычислить путь.", "top-right", "#FF5B5B", "error");
                }
            }
        });
    }

    show_way(way) {
        let edges = [];
        for (let i in this.#edges) {
            let from = this.#edges[i]["from"];
            let to = this.#edges[i]["to"];
            let edge = {"from": from, "to": to}
            for (let j = 0; j < way.length - 1; j++) {
                if ((from === way[j] && to === way[j + 1]) || (to === way[j] && from === way[j + 1])) {
                    edge["color"] = {color: 'blue'};
                    break;
                }
            }
            edges.push(edge);
        }
        this.#edges = edges;
        this.#draw();
    }

    selectNode(node) {
        this.#network.selectNodes([node.id]);
    }
}

function setJewellNet(div_id) {
    $.ajax({
        type: "POST",
        url: '/api/networking/dataset',
        success: function (result) {
            const res = JSON.parse(result);
            if (res.success === true) {
                jewellNet = new JewellNet(div_id, res.nodes, res.edges);
            } else {
                $.NotificationApp.send("Связи", "Не удалось загрузить данные о связях.", "top-right", "#FF5B5B", "error");
            }
        }
    });
}

function search_nodes() {
    const query = document.getElementById("input_query").value;
    $('#search_table').DataTable().destroy();
    document.getElementById("card-table-net").innerHTML = "<div class=\"card-body\"><table id=\"search_table\" class=\"table table-striped dt-responsive nowrap w-100\"><thead><tr><th>Фамилия и Имя</th><th>Telegram</th></tr></thead></table></div>";
    let alert = document.getElementById("results_alert");
    alert.className = "w-auto alert";
    alert.innerHTML = "";
    $.ajax({
        type: 'POST',
        url: '/api/networking/search',
        data:
            {
                "query": query,
            },
        success: function (result) {
            const res = JSON.parse(result);
            if (res.success === true) {
                if (res.users.length === 0) {
                    alert.className = "w-auto ms-3 alert alert-primary";
                    alert.innerHTML = "По запросу <strong>" + query + "</strong> ничего не найдено.";
                    document.getElementById("card-table-net").innerHTML = "";
                } else {
                    if (query.length > 0) {
                        alert.className = "w-auto alert alert-success";
                        alert.innerHTML = "По запросу <strong>" + query + "</strong> найдено записей <strong>" + res.users.length + "</strong>.";
                    }
                    const table = $('#search_table').DataTable({
                        data: res.users,
                        columns: [
                            {
                                data: 'name'
                            },
                            {
                                data: 'telegram'
                            }
                        ],
                        autofill: true,
                        order: [[0, 'asc']],
                        buttons: true,
                        dom: 'Blfrtip',
                        buttons: [
                            {
                                text: 'Отсюда',
                                action: function () {
                                    let rows = table.rows({selected: true});
                                    if (rows.count() === 0) {
                                        $.NotificationApp.send("Связи", "Сначала надо выбрать строку.", "top-right", "#cc8057", "warning");
                                    } else {
                                        jewellNet.setStartVertex(rows.data()[0].id);
                                    }
                                }
                            },
                            {
                                text: 'Сюда',
                                action: function () {
                                    let rows = table.rows({selected: true});
                                    if (rows.count() === 0) {
                                        $.NotificationApp.send("Связи", "Сначала надо выбрать строку.", "top-right", "#cc8057", "warning");
                                    } else {
                                        jewellNet.setFinishVertex(rows.data()[0].id);
                                    }
                                }
                            }],
                        select: 'single',
                        lengthMenu: [10, 25, 50, 100],
                        language: {
                            "lengthMenu": "Показывать _MENU_ записей",
                            "zeroRecords": "Ничего не найдено",
                            "info": "Показано _PAGE_ из _PAGES_",
                            "infoEmpty": "Нет доступных записей",
                            "infoFiltered": "(отфильтровано из _MAX_  общих записей)",
                            "paginate": {
                                "first": "Первый",
                                "last": "Последний",
                                "next": "Следующий",
                                "previous": "Предыдущий"
                            },
                            "loadingRecords": "Загрузка...",
                            "processing": "",
                            "search": "Искать:",
                            "select": {
                                "rows": {
                                    "_": "",
                                    "1": ""
                                }
                            },
                        }
                    });
                    document.getElementsByClassName("dt-buttons")[0].classList.add("mb-3");
                    table.on('select', function (e, dt, type, indexes) {
                        const node = table.rows(indexes).data().toArray()[0];
                        jewellNet.selectNode(node);
                    });
                }
            } else {
                $.NotificationApp.send("Связи", "Не удалось найти пользователей.", "top-right", "#FF5B5B", "error");
            }
        }
    });
}


