if (section == 'admin') {
$(document).ready(function() {

    /*  удаление из "не принимать"  */
    $("button[name='del_bad_id']").on("click", function(event) {
        var bad_id = $(this).parents(".bad_id").text().slice(0, -2);
        var ask = confirm(`Вы действительно хотите удалить ${bad_id} ?`)
        if (ask) {
            data.type = "deleteBadId";
            data.bad_id = bad_id;
            post(data)
            .done(function(response) {
                $(event.target).parent().remove();
            })
            .fail(function(response) {
                alert (response.responseText)
            });
        }
    });

    /*  добавление в "не принимать"  */
    $("button[name='add_bad_id']").on("click", function(event) {
        var input = $("input", $(this).parents("div:first"));
        var bad_id = input.val();

        if (!bad_id.match(/^[0-9]+$/)) {
            alert("Вводите только цифры");
            input.val("");
            return false
        };

        data.type = "addBadId";
        data.bad_id = bad_id;
        post(data)
        .done(function(response) {$("#list").append(response)})
        .fail(function(response) {alert (response.responseText)})
        input.val("");
    });

    /*  показать расписание  */
    $("button[name='show']").on("click", function(event) {
        var id_action = $(this).parents("tr").attr('data-action');

        // если таблица уже запрашивалась и просто скрыта
        if ($("td > table").length) {
            show_table(event.target)
        } else {  // не запрашивалась
            data.type = "showAdmin";
            data.id_action = id_action;

            post(data)
            .done(function(response) {
                $(event.target).hide();
                $(event.target).parent().append(response);
                var b_upd = $("button[name='upd']", $(event.target).parents("tr"));
                b_upd.hide();
            })
            .fail(function(response) {
                alert (response.responseText)
            });
        };
     });

    /*  скрыть расписание  */
    $("body").on("click", "button[name='hide']", function(event) { hide_table(event.target) });

    /*  удаление времени  */
    $("body").on("click", "button[name='del_time']", function(event) {
        var time = $("input", $(this).parent()).val();
        var day = $("td:first", $(this).parents("tr:first")).text().slice(0, -1);
        var name_action = $("td:first", $(this).parents("tr:last")).text();
        var id_action = $(this).parents("tr:last").data("action");

        var ask = confirm(`Вы действительно хотите удалить ${name_action} в ${day} ${time}?`)
        if (ask) {
            data.type = 'delTime';
            data.id_action = id_action;
            data.day = day;
            data.time = time;

            post(data)
            .done(function(response) {
                $(event.target).parent().remove();
            })
            .fail(function(response) {
                alert (response.responseText)
            });
        }
    })

//
//    $("body").on("click", "button[name='btn_upd']", function(event) {
//        let tr = $(event.target).parents("tr");
//        let table = $("td:even > table", tr)[0];
//        console.log(table)
//    });

});
}
