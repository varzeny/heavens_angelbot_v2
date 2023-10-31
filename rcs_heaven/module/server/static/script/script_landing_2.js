

let target_x = 0;
let target_y = 0;


document.getElementById('div_map').addEventListener('contextmenu', function(event) {
    event.preventDefault(); // 기본 컨텍스트 메뉴 방지
    target_x = X;
    target_y = Y;
    var contextMenu = document.getElementById('customContextMenu');
    contextMenu.style.display = 'block';
    contextMenu.style.left = `${event.pageX}px`;
    contextMenu.style.top = `${event.pageY}px`;
});

// 사용자가 다른 곳을 클릭하면 컨텍스트 메뉴 숨김
document.addEventListener('click', function(event) {
    document.getElementById('customContextMenu').style.display = 'none';
});



async function moveUnit(x,y) {



    target = document.getElementById("lbl_name").innerHTML;
    console.log(target)

    if( target.trim() === "name" || target.trim() === "unit_coffee" ){
        console.log("대상이 없음");
        return;
    }

    console.log("이동 시작!");

    var now = new Date().toISOString();

    let act = {
        "why": "request",
        "where": target,
        "what": "move",
        "how": `gotoPoint ${target_x} ${target_y}`,
        "who": "front",
        "when":now
    };


    let work = {
        "why": "request",
        "where": "rcs",
        "what": "work",
        "how": [ JSON.stringify( act ) ],
        "who": "front",
        "when":now
    };

    // console.log(data);
    await f2b_json( JSON.stringify(work) );
}