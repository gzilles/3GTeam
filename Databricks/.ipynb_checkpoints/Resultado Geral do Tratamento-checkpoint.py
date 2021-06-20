# Databricks notebook source
# Read parquet

parquetFile = spark.read.parquet("data/rais/")

# COMMAND ----------

# Create view

parquetFile.createOrReplaceTempView("parquetFile")

# COMMAND ----------

# Clean data

clean = spark.sql("""
SELECT
  CAST(Ano AS int),
  Sexo_Trabalhador,
  CAST(Idade AS int),
  CAST(Escolaridade_apos_2005 AS int),
  CNAE_2_0_Classe,
  CNAE_2_0_Subclasse,
  Tipo_Vinculo,
  CAST(Qtd_Hora_Contr AS int),
  Ind_Trab_Intermitente,
  CAST(REPLACE(Vl_Remun_Media_Nom, ',', '.') AS float) AS Vl_Remun_Media_Nom,
  UF
FROM parquetFile
""")

# COMMAND ----------

# Create view

clean.createOrReplaceTempView("clean")

# COMMAND ----------

# Transform data

tratato = spark.sql("""
SELECT
  CAST(Ano AS int),
  Sexo_Trabalhador,
  CAST(Idade AS int),
  CAST(Escolaridade_apos_2005 AS int),
  CNAE_2_0_Classe,
  CNAE_2_0_Subclasse,
  Tipo_Vinculo,
  CAST(Qtd_Hora_Contr AS int),
  Ind_Trab_Intermitente,
  CAST(REPLACE(Vl_Remun_Media_Nom, ',', '.') AS float) AS Vl_Remun_Media_Nom,
  UF
FROM clean
""")

# COMMAND ----------

# Create view tratado

tratato.createOrReplaceTempView("tratato")

# COMMAND ----------

tratato.write.parquet(f'refined/rais/Ano=2019/UF={estado}').partitions('UF', 'Ano')

# COMMAND ----------

# Read parquet

parquetFile = spark.read.parquet("data/rais/")

# COMMAND ----------

# Pergunta 1

spark.sql("""
SELECT
  Ano,
  Sexo_Trabalhador,
  AVG(Vl_Remun_Media_Nom)
FROM tratato
WHERE (CNAE_2_0_Classe LIKE '62%'
OR CNAE_2_0_Classe LIKE '631%') AND (UF = 'SP' OR UF = 'RJ' OR UF = 'MG' OR UF = 'ES')
GROUP BY Ano,
         Sexo_Trabalhador
ORDER BY Ano, Sexo_Trabalhador
""").show(5)

# COMMAND ----------

# Pergunta 2

spark.sql("""
SELECT
  Ano,
  Escolaridade_apos_2005,
  AVG(Vl_Remun_Media_Nom)

FROM tratato
WHERE (CNAE_2_0_Classe LIKE '011%'
OR CNAE_2_0_Classe LIKE '012%'
OR CNAE_2_0_Classe LIKE '013%'
OR CNAE_2_0_Classe LIKE '014%'
OR CNAE_2_0_Classe LIKE '015%'
OR CNAE_2_0_Classe LIKE '016%') AND (UF = 'RS' OR UF = 'SC' OR UF = 'PR') 
GROUP BY Ano,
         Escolaridade_apos_2005
ORDER BY Ano, Escolaridade_apos_2005
""").show(5)

# COMMAND ----------

# Grupo Saude

saude = spark.sql("""
SELECT
  Ano,
  Escolaridade_apos_2005,
  Vl_Remun_Media_Nom,
  Qtd_Hora_Contr,
  'proﬁssionais da saúde' AS Setor
FROM tratato
WHERE CNAE_2_0_Classe LIKE '86%'
OR CNAE_2_0_Classe LIKE '87%'
OR CNAE_2_0_Classe LIKE '88%'
""")

saude.createOrReplaceTempView("saude")

# COMMAND ----------

# Pergunta 3

spark.sql("""
SELECT
    Ano,
    Escolaridade_apos_2005,
    AVG(Vl_Remun_Media_Nom)
    
FROM
    saude
GROUP BY Ano, Escolaridade_apos_2005
ORDER BY Ano, Escolaridade_apos_2005
""").show(5)

# COMMAND ----------

# Grupo Tecnologia

tecnologia = spark.sql("""
SELECT
    Ano,
    Escolaridade_apos_2005,
    Vl_Remun_Media_Nom,
    Qtd_Hora_Contr,
    'tecnologia' AS Setor
    FROM tratato
    WHERE CNAE_2_0_Classe LIKE '62%' OR CNAE_2_0_Classe LIKE '631%'
""")

tecnologia.createOrReplaceTempView("tecnologia")

# COMMAND ----------

# Pergunta 3

spark.sql("""
SELECT
    Ano,
    Escolaridade_apos_2005,
    AVG(Vl_Remun_Media_Nom)
    
FROM
    tecnologia
GROUP BY Ano, Escolaridade_apos_2005
ORDER BY Ano, Escolaridade_apos_2005
""").show(5)

# COMMAND ----------

# Grupo Auto

auto = spark.sql("""
SELECT
  Ano,
  Escolaridade_apos_2005,
  Vl_Remun_Media_Nom,
  Qtd_Hora_Contr,
  'indústria automobilística' AS Setor
FROM tratato
WHERE CNAE_2_0_Classe LIKE '29%'
""")

auto.createOrReplaceTempView("auto")

# COMMAND ----------

# Pergunta 3

spark.sql("""
SELECT
  Ano,
  Escolaridade_apos_2005,
  AVG(Vl_Remun_Media_Nom)

FROM auto
GROUP BY Ano,
         Escolaridade_apos_2005
ORDER BY Ano, Escolaridade_apos_2005
""").show(5)

# COMMAND ----------

# Pergunta 4

spark.sql("""
SELECT
  ano,
  COUNT(1) AS qtd
FROM tecnologia
WHERE Qtd_Hora_Contr < 40
GROUP BY ano
ORDER BY ano
""").show()

# COMMAND ----------

# Pergunta 4

spark.sql("""
SELECT
  ano,
  COUNT(1) AS qtd
FROM auto
WHERE Qtd_Hora_Contr < 40
GROUP BY ano
ORDER BY ano
""").show()

# COMMAND ----------

# Pergunta 4

spark.sql("""
SELECT
  ano,
  count(1) as qtd
FROM saude
WHERE Qtd_Hora_Contr < 40
GROUP BY ano
ORDER BY ano
""").show()

# COMMAND ----------

# Pergunta 5

spark.sql("""
SELECT
  Ano,
  Sexo_Trabalhador,
  COUNT(1) AS qtd
FROM tratato
WHERE Ind_Trab_Intermitente = 1
GROUP BY Ano,
         Sexo_Trabalhador
ORDER BY Ano, Sexo_Trabalhador
""").show()