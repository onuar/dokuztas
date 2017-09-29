[![Build Status](https://travis-ci.org/onuar/dokuztas.svg?branch=master)](https://travis-ci.org/onuar/dokuztas)

# Dokuz taş
Türk geliştiriciler arasında Blockchain'in daha iyi anlaşılması için yapılmıştır. Proje hala yazım aşamasındadır. Sorularınız için Github'ın issues'ını kullanabilir ya da direkt [twitter@onurgil](https://twitter.com/onurgil) ile bana ulaşabilirsiniz.

## Versiyonlar
### 0.0.1
* Chain yaratma
* Genesis block ekleme
* Merkle root hash'inin hesaplanması
* Block ekleme
* Mining
* Mining için sırada bekleyen block'ları işleme
* Mining için sırada bekleyen block yoksa, txs'leri işlemeye geçme
* Node'ların ağa dahil olması
* Ağa sonradan dahil olan node'un, diğer node'lardan block'ları alması (sync)
* Problemi çözen miner'ın, ağdaki diğer node'ları haberdar etmesi

## Kurulum ve test

### Kurulum ihtiyaçları
    python 3.6.2
    virtualenv
    pip
> Homebrew ile kurmak işinizi kolaylaştıracaktır.

### Kurulum
    git clone https://github.com/onuar/dokuztas.git
    cd dokuztas
    virtualenv -p python3 dokuztas/venv
    source dokuztas/venv/bin/activate
    pip install -r requirements.txt

### Demo (Public nodes)
    source dokuztas/venv/bin/activate
    python dokuztas/nas.py
    python noderunner.py -p 5002
    python noderunner.py -p 5003 -m 1
    python noderunner.py -p 5004 -m 1
> 5003 ve 5004 miner olarak görev yapıyor (-m parametresi).
> 5003'ün ve 5004'ün farklı konfigürasyonlara sahip bilgisayarlar olma durumunu test edebilmek için, dokuztas.blockchain.Blockchain.mine metodundaki `Hardware spec simülasyonu` section'unu açabilirsiniz. Fakat unit test'ler çalıştırılırken, kapatılması unutulmamalıdır.

> Postman kullanıyorsanız, [postman_queries.json](https://github.com/onuar/dokuztas/blob/master/postman_queries.json) dosyasını import ederek direkt test etmeye başlayabilirsiniz.

### Demo (Ledger ve mining)
```python
source dokuztas/venv/bin/activate
python
>>> from dokuztas.blockchain import Blockchain, PendingBlock
>>> chain = Blockchain()
>>> chain._generate_genesis()
>>> new_block = PendingBlock()
>>> txs = ['Barış, Fırat\'a 100 coin gönderdi',
            'Fırat, İrgin\'e 50 coin gönderdi',
            'İrgin, Mert\'e 25 coin gönderdi',
            'Mert, Onur\'a 12,5 coin gönderdi',
            'Onur, Özgen\'e 6,25 coin gönderdi',
            'Özgen, Uğur\'a 3,125 coin gönderdi']
>>> new_block.add_txs(txs=txs)
>>> def always_run():
        return False
>>> chain.mine(pending_block=new_block, stop_mining_check = always_run)
```

### Testleri çalıştırmak için
    source dokuztas/venv/bin/activate
    pytest

## Açıklamalar
### node.mine()
İlk mine işleminin tetiklenmesi, 10 tx'in eklenip, 11. tx'in gelmesi ile başlamaktadır. Bu işlem tamamlandığında, sırada bekleyen block'lar varsa bunlar mine edilir, yoksa bekleyen txs'ler mine edilmeye başlanılır. Her bekleyen 10 tx, 1 block'un içine eklenerek bekletilir. Örn:
> 25 tane tx eklenmişse, 10'ardan iki tane block ve 5 tane block bekletilir. İlk olarak block'lar mine edilmeye başlanılır.

### blockchain.calculate_merkle(txs)
Root hash'i hesaplamak için her bir ikili elemanın hash'i alınır, bunlar ayrıca hashlenir. Eğer listedeki eleman sayısı tek sayı ise, sonuncu elemanın hash'i ayrıca hesaplanır. Çıkan hash'ler aynı fonksiyona parametre olarak tekrar gönderilir. Örn:
> 3 txs varsa 3. elemanın hashi ayrı hesaplanır, ilk iki elemanın hash'leri ayrı hesaplanır. hash_list'te iki tane hash olmuş olur. Bu iki hash'in de hash'lerinin hesaplanması için, fonksiyon tekrar çağırılır.
> 2 txs varsa, iki txs'in hash'leri hesaplanır ve bu hash'ler birleştirilerek tekrar hash alınır. Sonuç olarak elde tek hash vardır ve bu root hash olarak geri döndürülür.

### blockchain.mine()
sırada bekleyen txs'lerin merkle root hash'lerini hesaplamak ve block'a eklemek içindir.
 
## Yol haritası
* Windows ve Linux dağıtımlarından birinde test edilip, README sayfasının buna uygun değiştirilmesi.
* README'ye, bu projeye teknik anlamda nasıl destek verilebileceği ile ilgili bir bilgi eklemek.

### Eklenecek özellikler
* Bir miner ağa, pending txs'ler oluştuktan sonra dahil olduysa, aktif node'larda bu txs'leri alıp mining işlemine öyle başlamalıdır.
* Bir node ağa dahil olduğunda, ağa daha önceden bağlanmış olan node'lardan block'ları almalı ve en uygun (honest) block'u doğru olarak kabul etmeli. (consensus) (şu an için sadece ilk node'un chain'i alınıp, doğru kabul ediliyor.).
* Ağdaki node'ların block'ları manuple edemeyeceğini göstermek için, "/hack" adı altında bir resource eklenmesi. Bu /hack, basitçe mevcut block'taki bir tx'i değiştirip hash'leri tekrar hesaplayacak ve bu yeni chain'i diğer node'ların demokratik seçimine bırakacak. Sonuç olarak ağda dolaşan chain'in değiştirilemediği görülecek (immutability).
* Node Address Server olmadan da node'ların birbirinden haberdar olabilecekleri bir yapıya geçmek.
* (belki) Private ve public key'ler ile, tx'i ekleyen kişinin doğrulamasının yapılması.
* (belki) tx'lerin içerdiği data, cryptocurrency'lerde olduğu gibi from, to, amount içerecek şekilde değiştirilirse, double-spending engelleme kontrollerinin eklenmesi.