page_now=0;

$(document).ready(function(){
    $("#search_button").click(function(){
        text=$('#query').val()
        page_now=0
        search(text,page_now,1)
    });
});

$(document).ready(function(){
    $("#show_more").click(function(){
        page_now++;
        search(text,page_now,0)
    });
});

function search(text,page,flag){
    $.ajax({
        url:"search",
        method:"GET",
        data:{
            text:text,
            page:page
        },
        dataType:'json',
        success:function(result){
            if(flag){
                $("#result_box").empty()
            }
            $("#result_num").empty().append(result.num)
            append_str=''
            for(i=0;i<result.list.length;i++){
                page_obj=result.list[i]
                sub_title=page_obj.title
                sub_text=page_obj.text
                if(sub_title.length>20){
                    sub_title=sub_title.substring(0,20)+'...'
                }
                if(sub_text.length>180){
                    sub_text=sub_text.substring(0,180)+'...'
                }
                append_str+="<div class='result_page'>"+
                "<a class='result_title' href='"+page_obj.url
                +"'>"+sub_title
                +"</a><div class='page_info'>"+sub_text
                +"</div><a class='page_url'>"+page_obj.url
                +"</a></div>"
            }
            $("#result_box").append(append_str)
            
        }
    });
}