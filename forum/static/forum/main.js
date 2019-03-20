//  AJAX URLS

const UPVOTE_ANSWER_URL = "/upvote-answer/";
const UPVOTE_QUESTION_URL = "/upvote-question/";


/**
 * Tells whether a provided method is `csrf` safe or not.
 * @param {string} method The method to be used for data transfer.
 */
function csrfSafeMethod(method) { return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method)) };


/**
 * Setting `csrf_token` in the header.
 * Required when using `POST` AJAX requests.
 */
$.ajaxSetup({
    beforeSend: function (xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    },
    error: function (err) {
        console.log(err.responseText);
    }
});

$(function () {
    M.AutoInit();
    
    // Slider

    const slider = document.querySelector('.slider');
    
    M.Slider.init(slider,{
        indicators: false,
        height:500,
        transition: 300,
        interval: 6000
    });

    // For carousel inside question div
    $('.carousel.carousel-slider').carousel({
        fullWidth: true,
        indicators:true,
    });

    // 
    $('.dropdown-trigger').dropdown({
        constrainWidth: false,
        coverTrigger:false
    })

    // Focus the first input and textarea on every page reload
    $("input, textarea").first().focus();

    /**
     * Upvote answer
     * */
    $(".upvote-answer").click(function () {
   
        const upvote_btn = $(this);
        const upvote_count = upvote_btn.children(".upvote-count");
        const answer_id = upvote_btn.attr("data-answer");


        $.ajax({
            type: 'POST',
            url: UPVOTE_ANSWER_URL,
            data: {
                'answer_id': answer_id
            },
            success: function (count) {
                upvote_btn.toggleClass("upvoted");
                upvote_count.text(count);
            }
        })

    });

    $(".upvote-question").click(function () {
   
        const upvote_btn = $(this);
        const upvote_count = upvote_btn.children(".upvote-count");
        const question_id = upvote_btn.attr("data-question");


        $.ajax({
            type: 'POST',
            url: UPVOTE_QUESTION_URL,
            data: {
                'question_id': question_id
            },
            success: function (count) {
                upvote_btn.toggleClass("upvoted");
                upvote_count.text(count);
            }
        })

    });

    // Empty the value of answer field on every refresh
    $("#id_answer").val("");


})