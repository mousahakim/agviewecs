//custom objects


// chart function definitio 
function Chart() {
	// body...
}


Chart.prototype.makeChart = function(div, data, options) {
	// body...
	
};

Chart.prototype.addGraph = function(div, data, date_from) {
	// body...

};

Chart.prototype.changeDate = function(div, date_from) {
	// body...
};

Chart.prototype.refresh = function(div) {
	// body...
};

Chart.prototype.remove = function(div) {
	// body...
};



//Widget object

function Widget(widget, id, options) {
	// body...

	this.widget = widget; 
	this.id = id; 
	this.options = options;

}

Widget.prototype.create = function() {

	var new_widget = "";
	
	if (this.widget=='gis'){
		console.log('gis created');
		return
	}else if (this.widget=='sensor') {
		console.log('sensor created');
		return
	}else if (this.widget =='micro') {
		console.log('micro created');
		return
	}else if (this.widget =='grid')	{
		console.log('micro created');

		return


	}else if (this.widget =='weather') {
		console.log('weather created');

		return
	}else{
		console.log('custom created');

		return
	}

};

function addWidget () {
	widget = new Widget('gis', 2, {'code':'<div></div>'});
	widget.create();  
}

// var arr = []
// while(arr.length < 8){
//   var randomnumber=Math.ceil(Math.random()*100)
//   var found=false;
//   for(var i=0;i<arr.length;i++){
// 	if(arr[i]==randomnumber){found=true;break}
//   }
//   if(!found)arr[arr.length]=randomnumber;
// }
// document.write(arr);