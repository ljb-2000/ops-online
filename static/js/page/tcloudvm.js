/**
 * Created by weinan.zhao on 2015/5/28.
 */
$(function(){

    var vmKind = ["mini-1cpu-1mem","flavor-1core-2g","flavor-2core-4g","flavor-2core-16g","flavor-4core-8g","flavor-4core-16g","flavor-8core-16g"];
    var sectionDom = $("#vm_list");
    renderSectionList(sectionDom,vmKind);
    sectionDom.find(".section-item:first").addClass("active");
    var firstV = sectionDom.find(".section-item.active").attr("data-value");
   // console.log(firstV);
    $("#vmtype").val(firstV);
    $("#vm_list").on("click",".section-item",function(e){
        $("#vm_list>.section-item").removeClass("active");
        $(this).addClass("active");
        $("#vmtype").val($(this).attr("data-value"));
    });

    function renderSectionList(container,datas){
        if(container){
            var len = datas.length;
            var itm="";
            for(var i=0;i<len;i++){
                 itm+= "<div class='section-item' data-value='"+datas[i]+"'>"+datas[i]+"</div>";
            }
            container.append($(itm));
        }
    }

    $("#isPublicIP").toggles({
        drag: true, // allow dragging the toggle between positions
        click: true, // allow clicking on the toggle
        text: {
            on: 'ON', // text for the ON position
            off: 'OFF' // and off
        },
        on: false, // is the toggle ON on init
        animate: 250, // animation time
        transition: 'swing', // animation transition,
        checkbox: $("#publicip"), // the checkbox to toggle (for use in forms)
        width: 50, // width used if not set in css
        height: 20 // height if not set in css
    });

/*
    //disknum
     var disknum = $('#disknum').spinner();
    disknum.spinner('value',1);

    //disk size
     var disksize = $('#disksize').spinner();
     disksize.spinner('value',1);
*/

    $("input.number-require").on("keyup",function(e){
        var v = $(this).val();
        if(isNaN(v)){
            $(this).val("");
        }
    });

    //select checkbox
    $("#software").multipleSelect({
            multiple: true,width:"60%",
            placeholder:"选择软件类型"
        });

    //save back msg
    var msgDom = $("#save_back_msg");
    if(msgDom.length>0 && msgDom.val()){
        alert(msgDom.val());
    }


});