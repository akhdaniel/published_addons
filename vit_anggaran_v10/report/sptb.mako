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



</style>
</head>
<body>
% for sptb in objects:
<table width="100%">
	<tr>
		<th colspan="2">
			<h1>Surat Pernyataan Tanggung Jawab Belanja<br/>
				Nomor ${sptb.name}
			</h1>
		</th>
	</tr>
	<tr>
		<th width="40%">Nama Unit Kerja</th>
		<td>${sptb.unit_id.name}</td>
	</tr>
	<tr>
		<th>Jenis Belanja</th>
		<td>${sptb.jenis_belanja}</td>
	</tr>	
	<tr>
		<th>MAK/ Chart of Account</th>
		<td>${sptb.rka_detail_id.rka_coa_id.coa_id.name}</td>
	</tr>	
	<tr>
		<th>Kebijakan Renstra / Program</th>
		<td>${sptb.kebijakan_id.name}</td>
	</tr>	
	<tr>
		<th>Kegiatan</th>
		<td>${sptb.kegiatan_id.name}</td>
	</tr>	
</table>

<p>
	Yang bertanda tangan di bawah ini atasan langsung PUMKC ... menyatakan bahwa saya bertanggung jawab penus atas segala pengeluaran yang telah dibayar lunas oleh pemegang kas kepada yang berhak menerima dengan perincian: 
</p>

<table width="100%" class="rincian">
	<tr>
		<th class="rincian">Penerima</th>
		<th class="rincian">No NPWM</th>
		<th class="rincian">Uraian</th>
		<th class="rincian">Tgl Bukti</th>
		<th class="rincian">No Bukti</th>
		<th class="rincian">Jumlah</th>
	</tr>	
% for line in sptb.sptb_line_ids:
	<tr>
		<td class="rincian">${line.penerima_id.name}</td>
		<td class="rincian">${line.penerima_id.ref}</td>
		<td class="rincian">${line.uraian}</td>
		<td class="rincian">${line.bukti_tanggal}</td>
		<td class="rincian">${line.bukti_no}</td>
		<td class="rincian">${line.jumlah}</td>
	</tr>
% endfor

</table>

<p>&nbsp;</p>

<table width="100%">
	<tr>
		<td></td>
		<td></td>
		<td>Bandung, ${sptb.tanggal}</td>
	</tr>
	<tr>
		<td>
			Atasan Langsung PUMKC,
		</td>

		<td>
			Kasubag AFTIK
		</td>

		<td>
			PUMKC
		</td>
	</tr>
	<tr>
		<td style="height:150px">
			.........................<br/>
			${sptb.atasan_pumkc.name}<br/>
			${sptb.nip_atasan_pumkc}			
		</td>

		<td>
			.........................<br/>
			${sptb.kasubag_aftik.name}<br/>
			${sptb.nip_kasubag_aftik}					
		</td>

		<td>
			.........................<br/>
			${sptb.pumkc.name}<br/>
			${sptb.nip_pumkc}					
		</td>
	</tr>	
	<tr>
		<td colspan="3" style="text-align:center">Penerima</td>
	</tr>
	<tr>
		<td>
			Divisi Anggaran
		</td>
		<td></td>
		<td>
			Divisi Akuntansi
		</td>
	</tr>
	<tr>
		<td style="height:150px">
			.........................<br/>
			${sptb.div_anggaran.name}<br/>
			${sptb.nip_div_anggaran}			
		</td>
		<td></td>
		<td>
			.........................<br/>
			${sptb.div_akuntansi.name}<br/>
			${sptb.nip_div_akuntansi}					
		</td>
	</tr>	
</table>

% endfor
</body>
</html>