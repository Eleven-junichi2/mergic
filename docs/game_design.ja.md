# 仕様

## 概要

俯瞰視点の2D RPG。
魔法または技の連続発動による合成で異なる効果を楽しめる、
また、魔法の効果は入力した数値の性質によって変化する。

## グラフィック

16 x 16 のタイルマップ

## データ構造

tiletype_to_surf タイルの種類に対するpygame.Surfaceの辞書。str: pygame.Surface
assetname_to_filepath ファイルパスに対するエイリアス名辞書。 AssetFinderがこの役目を担う

## シナリオ

魔法使いの師弟が、無限に階数が続く塔or地下へ挑む。

## Integer Spell

このゲームのMagic（魔法）は、プレイヤーが自作することができる。
魔法は複数のtrait（特性）、一つのalchemical_element（属性）を持ち、その内容によって効果を分岐する。

魔法は生成関数を通して作成される。その引数にはinteger_spell（整数呪文、整数値）、strength（強さ）をとり、その整数の性質によって特性、属性が決定するのが独自の特徴。

プレイヤーはmp（マナ）を持ち、魔法を作成するごとに、その強さ分消費する。つまり、強さの最大値＝マナの最大値
マナは歩くごとに微量ずつ回復する。
魔法はspell（呪文）として自分でオリジナルの名前を付けて作成、スロットに保存することができる。
整数呪文は名前から生成することもできる。
非戦闘時以外でもアドリブで放つこともできる。アドリブで打つとマナの消費量が増える。
魔法の効果は整数呪文から推測する以外では、使うことで初めて発覚する。発覚した際、その内容がmemo（メモ）に記録される。このmemo（メモ）はいつでも編集できる。

魔法の合成

整数呪文同士はビット演算して合成することができる。

## ステータス

キャラクターは複数のresistance（耐性）を持つ。対応する種類の属性のダメージを受けるとき、その耐性が正なら被ダメージ軽減、負なら被ダメージ増加。

- name: str
- tag: str
- hp: int
  - max: int
  - current: int
- mp: int
  - max: int
  - current: int
- physical_ability: int
- armaments {head: , left_hand:, right_hand: , foot: , body: , accessory: ,}
- resistances {alchemical_element: resistance_value(float)}
- spells {name: {integer_spell: int, default_strength: int, memo: str}}
- status_effects set()

## 師弟システム

プレイヤーは二人組のパーティ（師弟）で、師匠として行動することになる。
弟子は交流値、機嫌のパラメータを持つ。
呪文スロットは弟子と師匠で共有。
戦闘時、弟子は行動選択の際、行動を提案する。採用すると機嫌が上がり、そのときの場面にその行動をしやすくなる。不採用だと、確率で機嫌が下がり、行動を提案せず勝手に動く確率が上がる。
戦闘を重ねたり、歩くほど交流値が増えていく。交流値が多いほど、ピンチの場面で助けになる行動を起こしてくれる。
プレイヤーが死ぬと、弟子が次の師匠＝プレイヤーとなる。弟子がいない状態でプレイヤーが死ぬとゲームオーバー。

## 戦闘

シンボルエンカウントで戦闘画面に移行する。
ターン性で行われる。基本的にはプレイヤーが先手だが、背後から接触されると敵が先手を取る。
行動順は身体能力が高い順で決まる。

### trait（特性）

|整数の条件|種類|説明|
|----|----|----|
|0|VOID（無属性）|効果に属性を付与する|
|正|LIGHT（光属性）|効果に属性を付与する|
|負|DARK（闇属性）|効果に属性を付与する|
|奇数|subtraction（減算）|受けた相手のHPを減算する|
|奇数かつ負|HEAT（炎属性）耐性|効果に属性耐性上昇を付与する|
|偶数|addition（加算）|受けた相手のHPを加算する|
|偶数かつ負|COLD（冷属性）耐性|効果に属性耐性上昇を付与する|
|10で割り切れる|confusion（混乱）|受けた相手は、次の行動の効果対象がランダムになる|
|1001で割り切れる|temptation（誘惑）|受けた相手は、次の行動の被対象が有利になる行動は対象をtemptationの送信元に変え、不利になる行動はtemptationの送信元に効果がないようにする。|
|ヴァンパイア数|vampire（吸血鬼）|発信者は、効果の被対象に与えたHPの減少分、発信者のそのHPを増加する。|
|ストロボマティック数|drowsiness（眠気）|受けた相手は、3ターンの間「眠気を催し、22%の確立で行動ができず、11%の確立でsleepを得る。」|
|ストロボマティック素数|sleep（眠り）|受けた相手は、3ターンの間眠る。ターン経過ごとに11%の確立で解除され、1ターン不眠状態になる。眠っていると何も行動できない。|
|四素合成数|random_elements（乱属性）|効果の属性がランダムになる（複数種類属性を持つこともある）。|
||stunスタン|1ターン行動できなくなる。|
|6|戦闘をstrengthで指定したターンまで巻き戻す。|
|666の倍数|demons_mercy悪魔の呪福|6ターンの間ランダムなデバフ1つを得る。このとき、他のデバフは解除される。|
|999の倍数|angels_msg天聲|9ターンの間確率でランダムなバフを得る。|
|レイランド数|HEAT||
|第2種レイランド数|COLD||
|五胞体数|poison（毒）|戦闘中5ターンの間最大HPの1/10ダメージを受ける|

整数の条件は、ダンジョンによっては変化する。

### プレイヤーターン

戦闘メニューから行動を選択できる。

- 足掻く
- 呪文
  - 今考える
  - スロットに登録した呪文を一覧表示
  - 選択時：
    - 今考えるのときは整数入力欄を表示
    - 込めるマナ：「」と入力させる
    - 最後に対象を選択
- 道具
- 身を守る
- 逃げる

足掻くと装備を頼りに戦う。効果はphysical_ability（身体能力）に依存する。
呪文から魔法を選ぶ。
道具から道具を選んで使用する。
身を守るを使うと、その次の被攻撃ターンだけ全属性の耐性をランダムな数値で得る。
逃げるとマナを消費する。マナが無いと逃げられない。戦闘を繰り返すほど必要な消費量が多くなる。

### 計算

被対象者をtarget、行動者をactorとする
commandに戦闘メニュー、もしくは敵AIによる行動選択を格納する。

#### 戦闘行動：足掻く

target.hp -= rng(actor.physical_ability) - rng(target.physical_ability)
actorのarmamentをそれぞれを調べ、それが持つtraitによってtargetもしくはactorに影響を与える。

#### 戦闘行動：呪文

##### 今考える

入力欄から受け取った整数値をinteger_spellに設定。文字列が代入されたらそれを整数値に変換して行う。

##### 込めるマナ

入力欄から受け取った整数値をstrengthに設定し、現在mpをstrengthで引く。今考える経由なら引く量は1.1倍

##### スロットから選択

選択した呪文のinteger_spellをinteger_spellに, default_strengthをstrengthにセットしてgenerate_magicを実行。
返されたMagic=actors_magicとする。

if actors_magic.traits has addition:
  effect_size = strength
  for alchemical_element in actors_magic.alchemical_elements:
    if target.registances has alchemical_element:
      effect_size *= (1 - target.registances[alchemical_element])
  target.hp += effect_size

if actors_magic.traits has confusion:
  target.status_effects.add(confusion)

といった具合。
