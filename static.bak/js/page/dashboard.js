/**
 * Created by weinan.zhao on 2015/5/28.
 */
 //dashborar chart1
      var uploads = [[0, 2], [1, 9], [2,5], [3, 13], [4, 6], [5, 13], [6, 8]];
	var downloads = [[0, 0], [1, 6.5], [2,4], [3, 10], [4, 2], [5, 10], [6, 4]];

	var plot = jQuery.plot(jQuery("#basicflot"),
		[{ data: uploads,
         label: "Uploads",
         color: "#1CAF9A"
        },
        { data: downloads,
          label: "Downloads",
          color: "#428BCA"
        }
      ],
      {
			series: {
				lines: {
					show: false
				},
				splines: {
					show: true,
					tension: 0.5,
					lineWidth: 1,
					fill: 0.45
				},
				shadowSize: 0
			},
			points: {
				show: true
			},
		  legend: {
          position: 'nw'
        },
		  grid: {
          hoverable: true,
          clickable: true,
          borderColor: '#ddd',
          borderWidth: 1,
          labelMargin: 10,
          backgroundColor: '#fff'
        },
		  yaxis: {
          min: 0,
          max: 15,
          color: '#eee'
        },
        xaxis: {
          color: '#eee'
        }
		});

    //chart2
     // Donut Chart
   var m1 = new Morris.Donut({
        element: 'donut-chart2',
        data: [
          {label: "Chrome", value: 30},
          {label: "Firefox", value: 20},
          {label: "Opera", value: 20},
          {label: "Safari", value: 20},
          {label: "Internet Explorer", value: 10}
        ],
        colors: ['#D9534F','#1CAF9A','#428BCA','#5BC0DE','#428BCA']
    });