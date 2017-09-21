[![Build Status](https://travis-ci.org/onuar/dokuztas.svg?branch=master)](https://travis-ci.org/onuar/dokuztas)

# Dokuz taş
Türk geliştiriciler arasında Blockchain'in daha iyi anlaşılması için yapılmıştır. Proje hala yazım aşamasındadır. Sorularınız için Github'ın issues'ını kullanabilir ya da direkt [twitter@onurgil](https://twitter.com/onurgil) ile bana ulaşabilirsiniz.

## İhtiyaçlar
    python 3.6.2
    virtualenv
    pip
> Homebrew ile kurmak işinizi kolaylaştıracaktır.

## Kurulum
    git clone https://github.com/onuar/dokuztas.git
    cd dokuztas
    virtualenv -p python3 dokuztas/venv
    source dokuztas/venv/bin/activate
    pip install -r requirements.txt

## Demo (Public nodes)
    source dokuztas/venv/bin/activate
    python dokuztas/nas.py
    python node-runner.py -p 5002
    python node-runner.py -p 5003
> todo: node.py ile dışarı açılan api'lerin dökümantasyonu yazılacak.

## Demo (Ledger)
```python
source dokuztas/venv/bin/activate
python
>>> from dokuztas.blockchain import Blockchain, Block
>>> chain = Blockchain()
>>> new_block = Block()
>>> chain.add_block(new_block)
```

# Testleri çalıştırmak için
    source dokuztas/venv/bin/activate
    pytest

# Yol haritası ve sonuç
> Öncelikle şunu belirtmem gerekiyor, proje henüz tamamlanmadı. Şu an için blockchain oluşturup, içersinde block'lar ekleyebiliyorsunuz. Bunun yanında node'ları sisteme dahil etmek de tamamlandı.

> Nas ve node için eksik testlerin yazılarak coverage'in artırılması gerekiyor.

> Kod içersindeki dökümantasyonun artırılması gerekiyor. Bunun sistematik bir şekilde ilerlemesi gerekiyor.

> Windows ortamında test edilip, README sayfasının buna uygun değiştirilmesi gerekiyor.

> README'ye, bu projeye teknik anlamda nasıl destek verilebileceği ile ilgili bir bilgi eklemek gerekiyor.

> Tamamlandığında yapılabilecekler:
    Yeni node eklemek (Checked!)
    Node'ların block ekleyebilmesi (Checked!)
    Miner'ların problemi çözme işlemleri (proof of work)
    Miner ödül sistemi
    Public ve private key'ler ile başka kullanıcılar adına işlem yapılmasını önlemek
    
# Açıklamalar
### node.mine
İlk mine işleminin tetiklenmesi, 10 tx'in eklenip, 11. tx'in gelmesi ile başlamaktadır. Bu işlem tamamlandığında, sırada bekleyen block'lar varsa bunlar mine edilir, yoksa bekleyen txs'ler mine edilmeye başlanılır. Her bekleyen 10 tx, 1 block'un içine eklenerek bekletilir. Örn:
> 25 tane tx eklenmişse, 10'ardan iki tane block ve 5 tane block bekletilir. İlk olarak block'lar mine edilmeye başlanılır.