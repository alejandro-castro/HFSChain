<?php
echo "*****************************************************************************************************************";
$doy=date("z")+1;
$year=date('Y');
$mon=date('m');
$mon = sprintf("%02d",$mon);
$day=date('d')-1;
$day = sprintf("%02d",$day);
$rxplaces = array("JRO","HUANCAYO","MALA","MERCED","BARRANCA","OROYA");
$rxstations = array("/HFTXANCON","/HFBTXANCON","/HFTXICA","/HFBTXICA","/HFTXSICAYA","/HFBTXSICAYA");
$days2review = MakeDaysArray(30);### REVISAR LOS 30 DIAS ANTERIORES A HOY
$tolerance = array("JRO"=>3,"HUANCAYO"=>13,"MALA"=>3,"MERCED"=>3,"BARRANCA"=>3,"OROYA"=>3);
$figureNum = array("JRO"=>10,"HUANCAYO"=>10,"MALA"=>4,"MERCED"=>4,"BARRANCA"=>4,"OROYA"=>3);

$asunto = "HF Warnning :".date("Y/m/d");
$from = "From: wmaster@jro-app.igp.gob.pe";
$mensaje = "Problema: Estaciones no presentan datos anteriores.\nRevisión del dia : /$year/$mon/$day \n";
$email = "josemaria.gomez@jro.igp.gob.pe,luis.vilcatoma@jro.igp.gob.pe,karim.kuyeng@jro.igp.gob.pe";
$dir = "/home/wmaster/web2/web_signalchain/data/";
$sendMail = 0;
echo "***Revision del :".$days2review[0]." al ".end($days2review)."******* \n";
foreach ($rxplaces as $place) # para cada receptor
{
	$dirp = $dir.$place;
	foreach($rxstations as $rx)# para cada transmisor
	{
		$rx_is_fixed = 0;
		$badday=0;
		$procdays=0;
		foreach($days2review as $d)
		{
			$dirf = $dirp.$rx."/$d/figures";
			$list = glob($dirf."/*.jpeg");
			$NumArchivos = count($list);
			if ($NumArchivos == $figureNum[$place])
			{
				if($d==$days2review[0])#if rx is fixed, dont send last bad days like warnning days
				{
					$rx_is_fixed = 1;
				}
			}
			else
			{
				$ans = SearchInDataLog($dirp,$d,$figureNum[$place]);
				#echo $d."ans=============>".$ans."\n";
				if($ans==1)
				{
					echo "Avaliable Data! \n";
					$procdays +=1;
				}
				elseif($ans==10||$ans==2||$ans==12)
				{
					echo "Avaliable Data! in A or B \n";
					$procdays +=1;
				}
				else
				{
					if($rx_is_fixed==0) # rx is no fixed, add one day to the warnning
					{
						$badday +=1;
					}
					else
					{
						echo "No Data but Rx Fixed \n";
					}
				}

			}
		}
		echo "Estación $rx ubicada en $place, tiene $badday dias atrasados y $procdays dias sin procesar.\n";
		if($badday>=$tolerance[$place] || $procdays>0)
		{
			$mensaje = $mensaje."Estación $rx ubicada en $place, tiene $badday dias atrasados y $procdays dias sin procesar.\n";
			$sendMail +=1;
		}

	}
}

if ($sendMail > 0 )
{
	mail($email,$asunto,$mensaje,$from);
}
else
{
	echo "$mensaje" ;
	echo "Revision Termianda, todo ok!";
}
echo "Trying to give permissions to web2/web_signalchain/data.";
$output = shell_exec('./datapermission.sh');

function MakeDaysArray($maxdays)
{
	$daysarray = array();
	for($i=1;$i<$maxdays;$i++)
	{
		$daysarray[] = date("Y/m/d",mktime(0,0,0,date('m'),date("d")-$i, date("Y")));
	}
	return $daysarray;
}

function SearchInDataLog($rxcode,$rxday,$Nfigures)
{
	$yearstr = explode('/',$rxday); # separate by / caracter
	$doynum= date("z",strtotime($rxday));
	#---DOY IN PHP STARTs AT 0 NO AT 1
	$doystr = sprintf("%03d",$doynum+1); # doy String with out d and year d20xxdoy
	$doystr = "d".$yearstr[0].$doystr;
	#echo "rxdir:========>".$rxcode."\n";
	if($Nfigures>=6)
	{
		#echo "Nfigures==:".$Nfigures." - doystr:".$doystr."\n";
		$rvalue = 99;
		if(count(glob($rxcode."/*.txt"))>0)
		{
		$file_linesA = file($rxcode."/avaliable_HFAdata.txt");
		$file_linesB = file($rxcode."/avaliable_HFBdata.txt");
		foreach($file_linesA as $line)
		{
			$eline=explode(' ',$line);
			try
			{	#echo "A-Comparing : ".$doystr."---".$eline[1]."-\n";
				if($doystr==$eline[1])# if data of the current doy is avaliable
				{
					#echo "finded : ".$doystr."-A\n";
					$rvalue=10;
					break;# stop if something is finded
				}
				else
				{
					$rvalue=0; #END: dont find avaliable data, means no data to show, means no add days to the warnning
				}
			}
			catch (Exception $e)
			{
				echo 'Excepción capturada: ',  $e->getMessage(), "\n";
			}
		}
		echo "Primera revision en A -";
		echo "rvalue:".$rvalue." \n";
		foreach($file_linesB as $line)
		{
			$eline=explode(' ',$line);
			try
			{	#echo "B-Comparing : ".$doystr."---".$eline[1]."-\n";
				if($doystr==$eline[1])# if data of the current doy is avaliable
				{	#echo "finded : ".$doystr."-B\n";
					#echo "rvalue:".$rvalue." \n";
					if ($rvalue ==10)
					{
						$rvalue=12;
					}
					else
					{
						$rvalue=2;
					}
					break;
				}
				else
				{
					if ($rvalue ==10)
					{
						$rvalue=10;
					}
					else
					{
						$rvalue=0;
					}
					#END: dont find avaliable data, means no data to show, means no add days to the wa$

				}
			}
			catch (Exception $e)
			{
				echo 'Excepción capturada: ',  $e->getMessage(), "\n";
			}
		}
		}
		else
		{
			echo "No data Log Avaliable.";
			return 0;
		}

		#echo "returnvalue FINAL :====>".$rvalue."\n";
		return $rvalue;
	}
	else
	{	#echo "Caso Normal";
		if(count(glob($rxcode."/*.txt"))>0)
		{
			$file_lines = file($rxcode."/avaliable_HFdata.txt");
			foreach($file_lines as $linen)
			{
				$elinen=explode(' ',$linen);
				#echo "elinen:".$elinen[1]."\n";
				#echo "elinen2:".$elinen[2]."\n";
				try
				{
					#echo "Comparing : ".$doystr."vs".$elinen[1]."\n";
					if($doystr==$elinen[1])# if data of the current doy is avaliable
					{
						#echo "finded : ".$doystr;
						return 1; #Future Work: this means that data must be procceced and sended to jro-app

					}

				}
				catch (Exception $e)
				{
					echo 'Excepción capturada: ',  $e->getMessage(), "\n";
				}
			}
			return 0; # nothing finded
		}
		else
		{
			echo "No data Log Avaliable.";
			return 0;
		}


	}
}
