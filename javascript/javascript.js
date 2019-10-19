$(document).ready(function(){
    // Trigger event on clicking button
    $("#submit_words").click(function(){
        send_input_words();
    });
    // Trigger event on pressing enter key
    $("#input_string").keypress(function(e){
        if(e.which == 13) {
            send_input_words();
        }
    });
    // Change name of dropdown when selecting language
    $("#language_selection li a").on('click', function(){
        selected_lang = $(this).text();
        new_text = selected_lang + '<span class="caret"></span>';
        $("#language").html(new_text);

    });
});

function send_input_words(){
    // Show waiting animation
    $('#loading').fadeIn();

    // Parse input string
    var input_string = $("#input_string").val();
    var words = input_string.split(" ");

    // Set options
    var lemma = $("#lemma").is(":checked");
    var stopwords = $("#stopwords").is(":checked");
    var language = $("#language").text().toLowerCase();

    // Retrieve data from server with GET
    var get_link = "webservice?words=" + words + "&language=" + language +  "&lemma=" + lemma + "&stopwords=" + stopwords;
    console.log(get_link);
    $.get(get_link, function(data, status){
        console.log('some data retrieved');
        console.log(data);
        // Display retrieved text results
        $("#result").text(data);
        // Parse retrieved JSON data
        var json = JSON.parse(data);
        $("#cooccurrences").text('visualization');

        // Hide waiting animation
        $('#loading').fadeOut('slow');
    });
}
