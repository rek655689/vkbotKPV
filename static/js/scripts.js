// Колхозный Фронтенд - BetweenAugust&December

var url =  new URL(location.href);
var section = url.pathname.slice(1)
var data = {section: section, vk_id: url.searchParams.get('id'), h: url.searchParams.get('h')};

/**
  * Переопределение jQuery ф-ции для переключения свойства hidden
  */
jQuery.fn.init.prototype.hide = function() {
    var state = $(this).prop("hidden");
    $(this).attr("hidden", !state);
};

/**
  * Отправка данных на сервер
  *
  * @param {object} data - данные для отправки
  * @param {function} do_error - функция, выполняющаяся в случае ошибки
  * @param {function} do_success - функция, выполняющаяся в случае успеха
  */
function post(data) {
    var jqxhr = $.ajax({
                    url: '/handler',
                    type: 'POST',
                    data: JSON.stringify(data),
                    contentType: 'application/json; charset=utf-8',
                });
    return jqxhr
};

/**
  * Скрыть таблицу
  */
function hide_table(b_hide) {
    $(b_hide).hide();
    $("button[name='show']", $(b_hide).parent()).hide();
    $("table", $(b_hide).parent()).hide();
    $("button[name='upd']", $(b_hide).parents("tr")).hide();
}

/**
  * Показать таблицу
  */
function show_table(b_show) {
    $(b_show).hide();
    $("button[name='hide']", $(b_show).parent()).hide();
    $("table", $(b_show).parent()).hide();
    $("button[name='upd']", $(b_show).parents("tr")).hide();
}

if (section == 'settings') {
$(document).ready(function() {

    /*  скрыть расписание  */
    $("body").on("click", "button[name='hide']", function(event) { hide_table(event.target) });

    $("button[name='show']").on("click", function(event) {
        let row = $(event.target).closest('tr')[0];
        let id_action = row.getAttribute('data-action');

        if (event.target.getAttribute("data-category") == "now") {
            let data = {type: 'showNow', id_action: id_action, vk_id: vk_id, h: h}

            if ($("table", row).length) {
                let button_show = event.target;
                let td = $(button_show).parent();
                let button_hide = $("button[name='btn_hide']", td)[0];
                let button_upd = $("button[name='btn_upd']", td.parent())[0];
                let table = $("table", td)[0];

                [button_hide, button_show, button_upd, table].forEach(function(elem) {
                    if (elem) {elem.hidden = !elem.hidden;}
                });
            } else {
                $.ajax({
                    url: '/handler',
                    type: 'POST',
                    data: JSON.stringify(data),
                    contentType: 'application/json; charset=utf-8',
                    error: function(xhr) {
                        alert (xhr.statusText);
                        },
                    success: function(response) {
                        let button_show = event.target;
                        button_show.hidden = !button_show.hidden;
                        $(button_show).parent().append(response);

                        let button_upd = $("button[name='btn_upd']", button_show.closest("tr"))[0];
                        if (button_upd) {button_upd.hidden = !button_upd.hidden;}
                        }
                });
            };
        };

        if (event.target.getAttribute("data-category") == "av") {
            let data = {type: 'showAv', id_action: id_action, vk_id: vk_id, h: h}

            if ($("table", row).length) {
                let button_show = event.target;
                let td = $(button_show).parent();
                let button_hide = $("button[name='btn_hide']", td)[0];
                let button_add = $("button[name='btn_add']", td.parent())[0];
                let table = $("table", td)[0];

                [button_hide, button_show, button_add, table].forEach(function(elem) {
                    if (elem) {elem.hidden = !elem.hidden;}
                });
            } else {
                $.ajax({
                    url: '/handler',
                    type: 'POST',
                    data: JSON.stringify(data),
                    contentType: 'application/json; charset=utf-8',
                    error: function(xhr) {
                        alert (xhr.statusText);
                        },
                    success: function(response) {
                        let button_show = event.target;
                        button_show.hidden = !button_show.hidden;
                        $(button_show).parent().append(response);

                        let button_add = $("button[name='btn_add']", button_show.closest("tr"))[0];
                        if (button_add) {button_add.hidden = !button_add.hidden;}
                        }
                });
            };
        };
    });

//    $("td").on("click", "button[name='hide']", function(event) {
//        let button_hide = event.target;
//        let td = $(button_hide).parent();
//        let button_show = $("button[name='show']", td)[0];
//        let table = $("table", td)[0];
//
//        if (event.target.getAttribute("data-category") == "now") {
//            let button_upd = $("button[name='upd']", td.parent())[0];
//            [button_hide, button_show, button_upd, table].forEach(function(elem) {
//                if (elem) {elem.hidden = !elem.hidden;}
//            });
//        };
//
//        if (event.target.getAttribute("data-category") == "av") {
//            let button_add = $("button[name='add']", td.parent())[0];
//            [button_hide, button_show, button_add, table].forEach(function(elem) {
//                if (elem) {elem.hidden = !elem.hidden;}
//            });
//        };
//    });

    $("td").on("change", "input[name='sch_time']", function(event) {
        let select = $("select", $(event.target).parent())[0];
        select.disabled = !select.disabled;
    });

    $("td").on("click", "button[name='btn_upd']", function(event) {
        let checked = $("input:checked", $(event.target).closest("tr"));
        let for_del = [];
        Array.from(checked).forEach(function(elem) {
           for_del.push(elem.getAttribute("value").slice(3));
        });

        let values = $("td > table", $(event.target).closest("tr")).find("div[name='sch_select']");
        let change_time = new Map();
        Array.from(values).forEach(function(elem) {
            let id = $("input", elem).prop("value").slice(3);
            let time = $("select", elem).val();
            change_time.set(id, time);
        });

        let data = {type: 'update', for_del: for_del, change_time: Array.from(change_time.entries()), vk_id: vk_id,
                    h: h};
        $.ajax({
                url: '/handler',
                type: 'POST',
                data: JSON.stringify(data),
                contentType: 'application/json; charset=utf-8',
                error: function(xhr) {
                    alert (xhr.statusText);
                    },
                success: function(response) {
                    let table = $("table", $(event.target).closest("tr"))[0];
                    let button_show = $("button[name='btn_show']", $(event.target).closest("tr"))[0];
                    let button_hide =$("button[name='btn_hide']", $(event.target).closest("tr"))[0];

                    table.remove();
                    button_hide.remove();
                    button_show.hidden = !button_show.hidden;
                    event.target.hidden = true;
                    }
            });

    });

    $("td").on("click", "button[name='btn_add']", function(event) {
        let values = $("td > table", $(event.target).closest("tr")).find("div[name='sch_select']");
        let add_actions = new Map();
        Array.from(values).forEach(function(elem) {
            if ($("input", elem)[0].disabled == false && $("input", elem)[0].checked == true) {
                let id = $("input", elem).prop("value").slice(3);
                let time = $("select", elem).val();
                add_actions.set(id, time);
            }
        });

        let data = {type: 'add', add_actions: Array.from(add_actions.entries()), vk_id: vk_id, h: h};
        $.ajax({
                url: '/handler',
                type: 'POST',
                data: JSON.stringify(data),
                contentType: 'application/json; charset=utf-8',
                error: function(xhr) {
                    alert (xhr.statusText);
                    },
                success: function(response) {
                    let table = $("table", $(event.target).closest("tr"))[0];
                    let button_show = $("button[name='btn_show']", $(event.target).closest("tr"))[0];
                    let button_hide =$("button[name='btn_hide']", $(event.target).closest("tr"))[0];

                    table.remove();
                    button_hide.remove();
                    button_show.hidden = !button_show.hidden;
                    event.target.hidden = true;
                    }
            });
    });

    $("button[data-rank='unique']").on("click", function(event) {
        if (event.target.getAttribute("name") == "btn_add") {
            let add = new Map();
            $("div[name='unique_add']").each(function() {
                if ($("input", this)[0].disabled == false && $("input", this)[0].checked == true) {
                    let id = $("input", this).prop("value").slice(1);
                    let time = $("select", this).val();
                    add.set(id, time);
                }
            });

            let url =  new URL(location.href);
            let vk_id = url.searchParams.get('id');
            let h = url.searchParams.get('h');
            let data = {type: 'add_unique', add: Array.from(add.entries()), vk_id: vk_id, h: h};

            $.ajax({
                url: '/handler',
                type: 'POST',
                data: JSON.stringify(data),
                contentType: 'application/json; charset=utf-8',
                error: function(xhr) {
                    alert (xhr.statusText);
                },
                success: function(response) {
                    location.reload()
                }
            });
        };

        if (event.target.getAttribute("name") == "btn_upd") {
            let for_del = []

            $("div[name='unique_upd'] > input:checked").each(function() {
                for_del.push(this.getAttribute("value").slice(1))
            });

            let values = $("div[name='unique_upd']");
            let change_time = new Map();
            Array.from(values).forEach(function(elem) {
                let id = $("input", elem).prop("value").slice(1);
                let time = $("select", elem).val();
                change_time.set(id, time);
            });


            let data = {type: 'update_unique', for_del: for_del, change_time: Array.from(change_time.entries()), vk_id: vk_id,
                        h: h};
            $.ajax({
                url: '/handler',
                type: 'POST',
                data: JSON.stringify(data),
                contentType: 'application/json; charset=utf-8',
                error: function(xhr) {
                    alert (xhr.statusText);
                },
                success: function(response) {
                    location.reload()
                }
            });
        };
    });

});
}