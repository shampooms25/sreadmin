import psycopg2

# Conectar ao banco
conn = psycopg2.connect(
    host='localhost',
    database='radiusd', 
    user='postgres',
    password='123.1234'
)

cur = conn.cursor()

# Verificar estrutura da tabela
cur.execute("""
    SELECT column_name, data_type, is_nullable 
    FROM information_schema.columns 
    WHERE table_name = 'eld_upload_videos'
    ORDER BY ordinal_position
""")

print("Estrutura da tabela eld_upload_videos:")
print("=" * 50)
for row in cur.fetchall():
    print(f"{row[0]}: {row[1]} (nullable: {row[2]})")

# Verificar se a tabela tem dados
cur.execute("SELECT COUNT(*) FROM eld_upload_videos")
count = cur.fetchone()[0]
print(f"\nTotal de registros: {count}")

if count > 0:
    # Verificar tipos de dados dos registros existentes
    cur.execute("SELECT id, tamanho FROM eld_upload_videos LIMIT 3")
    print("\nPrimeiros registros:")
    for row in cur.fetchall():
        print(f"ID: {row[0]}, Tamanho: {row[1]} (tipo: {type(row[1])})")

conn.close()
