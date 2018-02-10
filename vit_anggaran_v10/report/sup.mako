<html>
<head>
<style type="text/css">
${css}
body, p { font-size: 12pt }
th {text-align: left;}
</style>
</head>
<body>
% for sup in objects:
<table width="100%">
	<tr>
		<th>Nomor</th><th>${sup.name}</th>
	</tr>
	<tr>
		<th>Lampiran</th><th>${sup.lampiran}</th>
	</tr>
	<tr>
		<th>Perihal</th><th>${sup.perihal}</th>
	</tr>
	<tr>
		<th>Kepada</th><th>${sup.kepada}</th>
	</tr>
</table>
<p>
	Berdasarkan RKAT yang telah ditetapkan oleh Majelis Wali Amanat Nomor ${sup.dasar_rkat} bersama ini kami ajukan permintaan uang persediaan (UP) sebagai beikut: 
</p>

<table width="100%">
	<tr>
		<td>1</td>
		<td>Jumlah yang dimintakan</td>
		<td>${sup.jumlah}</td>
	</tr>
	<tr>
		<td>2</td>
		<td>Atas nama</td>
		<td>${sup.atas_nama.name}</td>
	</tr>
	<tr>
		<td>3</td>
		<td>Mempunyai rekening</td>
		<td>Nomor ${sup.nomor_rek}</td>
	</tr>
	
	<tr>
		<td>4</td>
		<td>Pada Bank</td>
		<td>Nomor ${sup.nama_bank}</td>
	</tr>
</table>

<p>&nbsp;</p>
<table width="100%">
	<tr>
		<td></td>
		<td>Bandung, ${sup.tanggal}</td>
	</tr>
	<tr>
		<td>
			Mengetahui<br>
			Atasan Langsung PUMKC,
		</td>

		<td>
			PUMKC
		</td>
	</tr>
	<tr>
		<td style="height:200px">
			.........................<br/>
			${sup.atasan_pumkc.name}<br/>
			${sup.nip_atasan_pumkc}			
		</td>

		<td>
			.........................<br/>
			${sup.pumkc.name}<br/>
			${sup.nip_pumkc}					
		</td>
	</tr>	
</table>

% endfor
</body>
</html>