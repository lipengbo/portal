function count(data){
	var sum = 0;
	for(var i=0; i<data.length; i++){
		sum += data[i];
	}
	return sum;
}

function data_process(data){    
    if (data > 1024){
		data = data/1024 //KB
        if (data > 1024){
			data = data/1024 //MB
            if (data >1024){
				data = data/1024 //GB
			}
		}
	}
    return Math.round(data);
}

function data_process_unit(data, unit){
    if (data > 1024){
		data = data/1024 //KB
        unit = 'KB'
        if (data > 1024){
			data = data/1024 //MB
            unit = 'MB'
            if (data >1024){
				data = data/1024 //GB
                unit = 'GB'
			}
		}
	}
    return unit
}


//data[0] = recv_data, data[1] = send_data, data[2] = unit, default is bit
function data_process_for_Y(data){
	if(data[0] > 1024 && data[1] > 1024){
		data[0] = data[0]/1024;
		data[1] = data[1]/1024;
		data[2] = 'KB';
		if(data[0] > 1024 && data[1] > 1024){
			data[0] = data[0]/1024;
			data[1] = data[1]/1024;
			data[2] = 'MB';
			if(data[0] > 1024 && data[1] > 1024){
				data[0] = data[0]/1024;
				data[1] = data[1]/1024;
				data[2] = 'GB';
			}
		}
	}
	return data;
} 



function math_round(data){
	return Math.round(data*100)/100;
}

function checkTime(i)
{
if (i<10) 
  {i="0" + i}
  return i
}

function clock()
{
	var today=new Date()
	var h=today.getHours()
	var m=today.getMinutes()
	var s=today.getSeconds()
	// add a zero in front of numbers<10
	m=checkTime(m)
	s=checkTime(s)
	return h+":"+m+":"+s
}


