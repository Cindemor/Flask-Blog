var initial = document.getElementsByClassName("search_choose");
var num = document.getElementsByTagName("th").length;
var initial_list = new Array();
var j = 0;
for(var l = 0; l < initial.length; l++)
{
    var initial_siblings = initial[l].parentNode.childNodes;
    for(var i = 1; i < initial_siblings.length; i+=2)
    {
        if(i != initial_siblings.length - 2)
            initial_list[j++] = initial_siblings[i].innerText;
        else{
            initial_list[j++] = initial_siblings[i].getElementsByTagName("input")[0].value;
            initial_list[j++] = initial_siblings[i].getElementsByTagName("input")[1].value;
        }
    }
}

function calendar(y, m, d)
{
    var myDate = new Date();
    m = String(m)
    d = String(d)
    if(m.length == 1)
        m = "0" + m
    if(d.length == 1)
        d = "0" + d
    document.getElementById("date").value = y + "-" + m + "-" + d + " " + myDate.getHours() + ":" + myDate.getMinutes() + ":" + myDate.getSeconds();
}
function search()
{
    var value = document.getElementById("search_text").value;
    var Re = new RegExp("^.*?" + value + ".*?$");
    var show_list = "";
    var show = document.getElementById("tag_list_body");
    for(var i = 0; i < initial_list.length; i+=(num+1))
    {
        if(Re.test(initial_list[i]))
        {
            show_list += "<tr>            \
            <td class=\"search_choose\"> \
            <div>";
            show_list += initial_list[i];
            show_list += "</div>\
            </td>";
            for(var m = 1; m < num; m++)
            {
                if(m <= num-2)
                show_list += " <td>\
                <div>" + initial_list[i+m] + "</div>\
                </td>"
                else
                {
                    show_list += "<td>"
                    show_list += "<input type=\"submit\" class=\"edit\" value=\"" + initial_list[i+m] + "\" />"
                    show_list += "<input type=\"submit\" class=\"delete\" value=\"" + initial_list[i+m+1] + "\" />"
                }
            }
            show_list += "</td>\
            </tr>"
        }
    }
    show.innerHTML = show_list;
}

function funny()
{
    alert("提交成功（由后端完成）");
}