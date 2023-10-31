const REALSIZE = 65400;
const MISX = 33500;
const MISY = -6000;
let MONITORSIZE = 1;
let MAPRATE = 1;

let X = 0;
let Y = 0;

let UNITS = {};

updateData();


document.getElementById('map').addEventListener('mousemove', function(e) {
    X = Math.floor( e.offsetX*MAPRATE-MISX );
    Y = Math.floor( e.offsetY*(-1)*MAPRATE-MISY );

    // // 이미지 위의 마우스 위치를 콘솔에 출력
    // console.log(`x: ${x}, y: ${y}`);

    // 위에서 생성한 div 요소에 마우스 위치를 표시 (옵션)
    document.getElementById('mousePosition').innerText = `x: ${X}, y: ${Y}`;
});


/////////////////////////////////////////////////////////////////////////
async function addMsg2Work(){
    jsonData = {
        "name": document.getElementById("input_msgName").value,
        "why": document.getElementById("input_why").value,
        "where": document.getElementById("input_where").value,
        "what": document.getElementById("input_what").value,
        "how": document.getElementById("input_how").value,
        "who": document.getElementById("input_who").value,
        "when": document.getElementById("input_when").value
        };
    console.log(jsonData);


    div = document.createElement("div");
    div.id = jsonData["name"];
    div.innerText = jsonData["name"];
    div.dataset.msg = JSON.stringify(jsonData);
    
    // 버튼 1 생성 및 설정
    let button1 = document.createElement("button");
    button1.innerText = "제거";
    button1.onclick = function() {
        console.log("버튼 1 클릭됨");
        this.parentNode.remove();
    };
    div.appendChild(button1);

    // 버튼 2 생성 및 설정
    let button2 = document.createElement("button");
    button2.innerText = "버튼 2";
    button2.onclick = function() {
        console.log("버튼 2 클릭됨");
    };
    div.appendChild(button2);

    
    document.getElementById("work_cmd").appendChild(div);
}

/////////////////////////////////////////////////////////////////////////
async function addWork2List(){
    const list_work = [];

    // "work_cmd" 요소 내부의 모든 div 요소들을 선택합니다.
    const divs = document.getElementById("work_cmd").querySelectorAll("div");

    // 각 div 요소에 대해 반복을 수행하면서 dataset.msg 값을 배열에 추가합니다.
    divs.forEach(div => {
        if(div.dataset.msg) {
            list_work.push(div.dataset.msg);
        }
    });
    // console.log(list_work);  // 확인용

    /////////////////////////////

    let data_d = {
        "why": "request",
        "where": "rcs",
        "what": "work",
        "how": list_work,
        "who": "front",
        "when": "now"
        };

    
    let divv = document.createElement("div");

    divv.innerText = document.getElementById("input_workName").value;
    divv.dataset.work = JSON.stringify(data_d);

    // 버튼 1 생성 및 설정
    let button1 = document.createElement("button");
    button1.innerText = "제거";
    button1.onclick = function() {
        console.log("버튼 1 클릭됨");
        this.parentNode.remove();
    };
    divv.appendChild(button1);

    // 버튼 2 생성 및 설정
    let button2 = document.createElement("button");
    button2.innerText = "실행";
    button2.onclick = async function(){
        await f2b_json(this.parentNode.dataset.work);
    };
    divv.appendChild(button2);


    document.getElementById("work_list").appendChild(divv);
}


async function f2b_json(inputdata=null) {
    let jsonString;
    
    if (inputdata !== null){
        jsonString = inputdata
    }else{
        let jsonData = {
        "why": document.getElementById("input_why").value,
        "where": document.getElementById("input_where").value,
        "what": document.getElementById("input_what").value,
        "how": document.getElementById("input_how").value,
        "who": document.getElementById("input_who").value,
        "when": document.getElementById("input_when").value
        };
        jsonString = JSON.stringify(jsonData);
    }

    try {
        // POST 요청을 보냅니다.
        const response = await fetch("/f2b_json", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: jsonString
        });

        const data = await response.json();
        console.log("Response:", data);
    } catch (error) {
        console.error("Error:", error);
    }
}



async function updateData(){////////////////////////////////
    while(1){

        try{
            const respone = await fetch("/updateData",{method:"POST"});
            const jsonData = await respone.json();
            UNITS = JSON.parse( jsonData );

            try{
                // console.log( UNITS );
                await updateUnits();

                // for( let name in units ){
                //     await updateUnit( name, units[name] );
                // }
                var now = new Date();
                document.getElementById("time").innerHTML = now;

            }
            catch(error){
                console.log( "유닛 표시중 오류" );
            }
        }

        catch(error){
            console.log( "에러발생",error );
        }

        finally{
            await new Promise(resolve => setTimeout( resolve,1000 ));
        }
    }
    
}////////////////////////////////////////////////////////////

async function updateUnits(){
    for (let name in UNITS){
        console.log( name,"====",UNITS[name] )

        if( document.getElementById(name) ){
            // console.log(name)
            MONITORSIZE = parseFloat( getComputedStyle( document.getElementById('map') ).width) 

            MAPRATE = REALSIZE / MONITORSIZE

  

            img = document.getElementById(name);
            img.style.left = `${ ( UNITS[name]['location']['x']+MISX )/MAPRATE }px`;
            img.style.top = `${ ( ( UNITS[name]['location']['y']+MISY )/MAPRATE)*(-1) }px`;
            img.style.transform = `rotate(${ 360-UNITS[name]['location']['theta'] }deg)`;

            if(document.getElementById('lbl_name').innerText == name){
                let data = UNITS[name];
                document.getElementById('lbl_flag_idle').innerText = data["flag_idle"];
                document.getElementById('lbl_work').innerText = data["work"];
                document.getElementById('lbl_work_n').innerText = data["work_n"];
                document.getElementById('lbl_parts').innerText = JSON.stringify(data["parts"]);
            
            }

        }else{
            console.log( "마커 추가",name );
            // console.log(name)
            img = document.createElement( 'img' );
            img.id = name;
            if(name[5] != "c"){
                img.src = "static/icon/angelbot.png";
                img.style.width = "20px";
                img.style.height = "20px";
            }
            else{
                img.src = "static/icon/coffee.png";
                img.style.width = "30px";
                img.style.height = "30px";
            }
            
            img.style.position = "absolute";
            img.style.left = "-100px";
            img.style.top = "-100px";
            img.style.transform = "rotate(0deg)";
            // img.setAttribute('data-info', "")
            img.onclick = await function(){
                const data = JSON.parse(this.getAttribute('data-info'));

                document.getElementById('lbl_name').innerText = this.id;
                
            }

            document.getElementById("div_map").appendChild( img );
        }
    }


    // async function updateTime

}


