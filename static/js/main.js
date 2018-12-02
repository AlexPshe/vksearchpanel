document.onkeydown = function (e) {
  e = e || window.event;
  switch (e.which || e.keyCode) {
        case 13 :
            var el = document.querySelector( ':focus' );
            if( el ) el.blur();
            document.getElementsByClassName("btn-search")[0].onclick();
  }
}

var button = document.getElementsByClassName("btn-search")[0];
button.onclick = function(){
    w = "#FCCACA";
    srch = document.getElementById("search");
    sentiment = document.getElementsByName("choices-single-defaul")[0];
    if(srch.value != "" && sentiment.value != "Feeling"){
        window.location = '/search/q?search=' + srch.value.toLowerCase() + '&sentiment=' + sentiment.value.toLowerCase();
    } else {
        if(srch.value == "" && sentiment.value != "Feeling"){
            document.getElementsByClassName("input-field first-wrap")[0].style.backgroundColor = "#fff"
            document.getElementsByClassName("input-field second-wrap")[0].style.backgroundColor = w
        } else if(sentiment.value == "Feeling" && srch.value != ""){
            document.getElementsByClassName("input-field second-wrap")[0].style.backgroundColor = "#fff"
            document.getElementsByClassName("input-field first-wrap")[0].style.backgroundColor = w
        } else {
            document.getElementsByClassName("input-field first-wrap")[0].style.backgroundColor = w
            document.getElementsByClassName("input-field second-wrap")[0].style.backgroundColor = w
        }
    }
}
