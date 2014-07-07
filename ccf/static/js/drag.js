var move=false;

function StartDrag(obj)                      

{

//if(event.button==1&&event.srcElement.tagName.toUpperCase()=="DIV")

//{
   document.getElementById("editInfoModal").SetCapture();

   //obj.style.background="#999";

   move=true;

//   }

}

 

function Drag(obj)                  

{

if(move)

{

    var oldwin=obj.parentNode;

    oldwin.style.left=event.clientX-50;

    oldwin.style.top=event.clientY-10;

}

}

 

function StopDrag(obj)

{

   //obj.style.background="#EEE";

   document.getElementById("editInfoModal").ReleaseCapture();

   move=false;

}

  

function closediv(obj){

obj.style.display="none";

}

function opendiv(obj){

obj.style.display="block";

}
