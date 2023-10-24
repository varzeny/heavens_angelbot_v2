


setInterval(show_unit, 1000)



///////////////////////////////////////////////////////////////////////

async function show_unit(){
    try{
        let response = await fetch("/showUnit");

        if(!response.ok){
            throw new Error("respone 에 문제있음! ${response.status}");
        }

        let data = await response.json();

        console.log(data);
    }catch(error){
        console.error("show_unit 에서 오류남!"+error.message);
    }
}



///////////////////////////////////////////////////////////////////////

async function addNode(){
    let jsonData = {
        "why": document.getElementById("input_why").value,
        "where": document.getElementById("input_where").value,
        "what": document.getElementById("input_what").value,
        "how": document.getElementById("input_how").value,
        "who": document.getElementById("input_who").value,
        "when": document.getElementById("input_when").value
        };
    
        nodes.push(newNode);
        updateSimulation();



}

//////////////////////////////////////////////////////////////////////////



let svg = d3.select("#work_tree")
            .append("svg")
            .attr("width", "100%")
            .attr("height", "100%");

let nodes=[];

let simulation = d3.forceSimulation(nodes)
    .force("charge", d3.forceManyBody().strength(-200))
    .force("center", d3.forceCenter(width / 2, height / 2))
    .force("collision", d3.forceCollide().radius(60))
    .on("tick", ticked);


let rootNode = svg.append("circle")
                  .attr("cx", "50%")
                  .attr("cy", "50%")
                  .attr("r", 10)
                  .attr("fill", "blue")
                  .attr("stroke", "black")
                  .datum(someData)  // 데이터 바인딩
                  .on("click", function() {
                      let boundData = d3.select(this).datum();  // 바인딩된 데이터 접근
                      console.log(boundData);
                  });
