function not_none(obj, i)
{
    if(obj.value == "")
    {
       if(i == 0)
        document.getElementById("informations" + i).innerText = "请按要求输入标题"
       else if(i == 1)
        document.getElementById("informations" + i).innerText = "请按要求输入文件名"

       document.getElementById("informations" + i).style.color = "red";     
       document.getElementById("informations" + i).style.marginTop = "5px";       
       document.getElementById("informations" + i).style.marginBottom = "0px";
       document.getElementsByClassName("notnone_text")[i].style.border = "1px solid red";
    }
    else
    {
        document.getElementById("informations" + i).innerText = ""
        document.getElementsByClassName("notnone_text")[i].style.border = "1px solid #999";
    }
}

function click_trans_change(string)
{
    if(string == "article")
    {
        document.getElementById("choice_1").parentNode.className = "active";
        document.getElementById("choice_1").className = "active";
        document.getElementById("choice_2").parentNode.className = "no_active";
        document.getElementById("choice_2").className = "no_active";
        document.getElementById("choice_3").parentNode.className = "no_active";
        document.getElementById("choice_3").className = "no_active";
        document.getElementById("choice_0").parentNode.className = "no_active";
        document.getElementById("choice_0").className = "no_active";
        document.getElementById("choice_4").parentNode.className = "no_active";
        document.getElementById("choice_4").className = "no_active";

        document.getElementById("change_1").style.display = "";
        document.getElementById("change_2").style.display = "none";
        document.getElementById("change_3").style.display = "none";
    }
    else if(string == "page")
    {
        document.getElementById("choice_2").parentNode.className = "active";
        document.getElementById("choice_2").className = "active";
        document.getElementById("choice_1").parentNode.className = "no_active";
        document.getElementById("choice_1").className = "no_active";
        document.getElementById("choice_3").parentNode.className = "no_active";
        document.getElementById("choice_3").className = "no_active";
        document.getElementById("choice_0").parentNode.className = "no_active";
        document.getElementById("choice_0").className = "no_active";
        document.getElementById("choice_4").parentNode.className = "no_active";
        document.getElementById("choice_4").className = "no_active";

        document.getElementById("change_2").style.display = "";
        document.getElementById("change_3").style.display = "none";
        document.getElementById("change_1").style.display = "none";
    }
    else
    {
        document.getElementById("choice_3").parentNode.className = "active";
        document.getElementById("choice_3").className = "active";
        document.getElementById("choice_1").parentNode.className = "no_active";
        document.getElementById("choice_1").className = "no_active";
        document.getElementById("choice_2").parentNode.className = "no_active";
        document.getElementById("choice_2").className = "no_active";
        document.getElementById("choice_0").parentNode.className = "no_active";
        document.getElementById("choice_0").className = "no_active";
        document.getElementById("choice_4").parentNode.className = "no_active";
        document.getElementById("choice_4").className = "no_active";

        document.getElementById("change_3").style.display = "";
        document.getElementById("change_2").style.display = "none";
        document.getElementById("change_1").style.display = "none";
    }
}

function selectbox(obj)
{
    var select_ul = document.getElementById("options");
    var select = document.getElementById("author");
    select.value = obj.innerText;
    select_ul.style.borderBottom = "";
    select_ul.style.display = "none";
}