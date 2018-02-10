<html>
<head>
<style type="text/css">
${css}
body, p { font-size: 12pt }
th {text-align: left;}
table.rincian, th.rincian, td.rincian  {
    border-collapse: collapse;
    border: 1px solid black;
}
.number {
 	text-align: right
}

</style>
</head>
<body>
% for spp in objects:
<h1>Surat Permintaan Pembayaran<br/>
	Nomor ${spp.name}
</h1>

<table width="100%"  class="rincian">
	<tr>
		<th class="rincian">TAMBAHAN UP (TUP)</th>
		<th class="rincian">PENGGUNAAN UP (SPP GUP)</th>
		<th class="rincian">PEMB LS (SPPR LS)</th>
	</tr>
</table>

<p>
	Kepada ${spp.kepada}
</p>

<p>
	Sesuai dengan RKAT yang telah ditetapkan oleh Majelis Wali Amanat Nomor ${spp.dasar_rkat} bersama ini kami ajukan permintaan pembayaran sebagai beikut: 
</p>

<table width="100%">
	<tr>
		<th width="40%">Jumlah pembayaran yang diminta</th>
		<td>${spp.jumlah}</td>
	</tr>
	<tr>
		<th>Untuk keperluan</th>
		<td>${spp.keperluan}</td>
	</tr>
	<tr>
		<th>MAK</th>
		<td>${spp.mak.name}</td>
	</tr>
	<tr>
		<th>Atas nama</th>
		<td>${spp.atas_nama.name}</td>
	</tr>
	<tr>
		<th>Alamat</th>
		<td>${spp.atas_nama.alamat}</td>
	</tr>
	<tr>
		<th>Mempunyai rekening</th>
		<td>Nomor ${spp.nomor_rek}</td>
	</tr>
	
	<tr>
		<th>Pada Bank</th>
		<td>${spp.nama_bank}</td>
	</tr>
</table>

<p>Dengan penjelasan:</p>


<table width="100%" class="rincian">
	<tr>
		<th class="rincian">COA</th>
		<th class="rincian">PAGU</th>
		<th class="rincian">SPP sd. yang Lalu</th>
		<th class="rincian">SPP Ini</th>
		<th class="rincian">Jumlah SPP sd. Ini</th>
		<th class="rincian">Sisa Dana</th>
	</tr>	
% for line in spp.spp_line_ids:
	<tr>
		<td class="rincian">${line.rka_detail_id.rka_coa_id.coa_id.name}</td>
		<td class="rincian number">${line.pagu}</td>
		<td class="rincian number">${line.spp_lalu}</td>
		<td class="rincian number">${line.spp_ini}</td>
		<td class="rincian number">${line.jumlah_spp}</td>
		<td class="rincian number">${line.sisa_dana}</td>
	</tr>
% endfor

</table>
<br/>
<table width="100%">
	<tr>
		<td></td>
		<td>Bandung, ${spp.tanggal}</td>
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
			${spp.atasan_pumkc.name}<br/>
			${spp.nip_atasan_pumkc}			
		</td>

		<td>
			.........................<br/>
			${spp.pumkc.name}<br/>
			${spp.nip_pumkc}					
		</td>
	</tr>	
</table>

% endfor
</body>
</html>