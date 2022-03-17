var MQ = MathQuill.getInterface(2);

var problemSpan = document.getElementById('problem');
var answer_box_div = document.getElementById('answer_box_div')
var answerSpan = document.getElementById('answer_box_#1');
var add_answer_box = document.getElementById('add_answer_box');
var remove_answer_box = document.getElementById('remove_answer_box');

MQ.StaticMath(problemSpan);

function get_user_answer() {

    user_answers = [];

    for (var i = 0; i < answer_math_fields.length; i++){
        user_answers[i] = answer_math_fields[i].latex();
    }
    document.getElementById('user_answer').value = user_answers;
}

answer_box_counter = 0
answer_math_fields = []

function create_answer_box(){
    var answer_box = document.createElement('span');
    answer_box.id = 'answer_box_#' + answer_box_counter;
    answer_box_div.appendChild(answer_box);
    answer_math_fields.push(MQ.MathField(answer_box));
}

function remove_answer_boxes(){
    var answer_box = document.getElementById('answer_box_#' + answer_box_counter);
    answer_box_div.removeChild(answer_box);
    answer_math_fields.pop()
}

add_answer_box.addEventListener('click', ()=> {
    answer_box_counter += 1;
    create_answer_box();
});

remove_answer_box.addEventListener('click', ()=> {
    if (answer_box_counter >= 0) {
        remove_answer_boxes();
        answer_box_counter -= 1;
    };
});

create_answer_box();
