function showMenu( idx )
{
    //first hide all other menus!
	$('div.l'+idx+'menu').css({'visibility':'visible'})
}

function hideMenu( idx )
{
	$('div.l'+idx+'menu').css({'visibility':'hidden'});
}

function setupMenu( idx )
{
	$('div.l'+idx+'menuFold').hover( function(){ showMenu(idx); }, function(){} );    
	$('div.l'+idx+'menu').hover( function(){}, function(){ hideMenu(idx); } );
}

$(function() {

    for( i = 1; i <=5; i++)
		setupMenu(i);
	   
});

