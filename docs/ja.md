# unknowns-workflow 日本語紹介

`unknowns-workflow` は、AIエージェントに実装を頼む前に「まだ何がわかっていないか」を整理するためのワークフローです。

AIにコードを書かせるとき、失敗の原因は「AIの実装力が低い」だけではありません。そもそも依頼文や計画の中に、まだ言語化されていない前提、未確認の仕様、コードベース特有の落とし穴が残っていることが多いです。

このワークフローは、そこを実装前に見つけるためのものです。

## 何を解決するものか

たとえば、AIにこう頼むとします。

```text
この設定画面をいい感じに直して
```

このままだと、AIは一般的な「いい感じ」を勝手に補ってしまいます。でも本当は、次のような未確認事項があるかもしれません。

- 既存アプリのデザイン密度はどれくらいか
- ユーザーは初心者向けなのか、業務で毎日使う人なのか
- 似た画面がすでにコードベースにあるのか
- 「派手にする」のではなく「情報を探しやすくする」のが目的なのか
- 変更してはいけない既存の動線があるのか

こういうものを実装後に見つけると、手戻りが大きくなります。`unknowns-workflow` は、実装前にそれらを分類して、必要なら質問・調査・プロトタイプに回します。

## 4つの unknowns

このワークフローでは、わかっていること・わかっていないことを4種類に分けます。

| 種類 | 意味 | 例 |
| --- | --- | --- |
| Known Knowns | すでにわかっていること | Reactを使っている。既存の設定画面がある。 |
| Known Unknowns | わかっていないと自覚していること | 状態をURLに持つべきか、ローカルstateでよいか。 |
| Unknown Knowns | 見れば判断できるが、まだ言葉になっていない基準 | 「これは業務ツールっぽくない」「このUIは軽すぎる」 |
| Unknown Unknowns | まだ誰も気づいていない落とし穴 | 既存の認証処理に特殊な更新順序がある。 |

特に重要なのは、**Unknown Unknowns** です。これは普通に計画しているだけでは出てきません。コードベースを読んだり、似た実装を探したり、先に小さなプロトタイプを作ったりして初めて見つかります。

## 使い方の流れ

基本の流れはこうです。

1. まず `finding-unknowns` で、今回の作業の未知を分類する。
2. 慣れていない領域なら `unknowns-blindspot` で、知らない落とし穴を先に探す。
3. UIや仕様の好みが曖昧なら `unknowns-brainstorm` で、複数案を出して反応できる形にする。
4. 明確な未決事項があるなら `unknowns-interview` で、実装に効く質問だけを一つずつ聞く。
5. 参考にしたい既存コードやサイトがあるなら `unknowns-references` で、何を真似して何を真似しないか整理する。
6. 実装中は `unknowns-impl-notes` で、計画と違った点を記録する。
7. 実装後、理解を深めたいなら `unknowns-quiz`、レビューや共有用に説明したいなら `unknowns-explainer` を使う。

## 具体例

依頼:

```text
新しいSSO対応を追加したい。でもこの認証周りのコードはよく知らない。
まずblindspot passをして、実装前に何を確認すべきか教えて。
```

この場合、いきなり実装せずに、AIにはまずこう調べさせます。

- 既存の認証フローはどこにあるか
- トークン更新やセッション管理に特殊な処理があるか
- テストで守られている仕様は何か
- 似た認証プロバイダの実装があるか
- 追加前に決めるべき設計判断は何か

そのあとで、実装に入ります。

## 何が嬉しいか

- AIへの依頼がうまくなる
- 実装前に手戻りの大きい問題を見つけやすくなる
- 「なんとなく違う」を言語化しやすくなる
- 長い実装のあとに、何が変わったのか理解しやすくなる
- レビュー時に「どんな未知があり、どう解決したか」を説明しやすくなる

## 向いている作業

- 初めて触るコードベース
- 認証、課金、データモデルなど失敗したときの影響が大きい実装
- UI/UXのように「見ればわかるが説明しづらい」作業
- 既存の実装パターンに合わせる必要がある変更
- AIに丸投げすると、一般論で実装されそうな作業

## 向いていない作業

単純な誤字修正や、1行だけの明らかな修正には大げさです。そういう場合は普通に直せば十分です。

## 導入方法

### ローカルプラグインマーケットプレイス

このリポジトリを、8つのスキルをすべてまとめた1つのローカルプラグインとしてインストールできます。リポジトリをローカルの安定したパスにクローンまたは配置し、そのルートディレクトリから以下を実行します。

```bash
codex plugin marketplace add .
codex plugin add unknowns-workflow@unknowns-workflow-local
```

マーケットプレイスを登録したら、ChatGPT デスクトップアプリを再起動してください。また、**Plugins**を開き、**Unknowns Workflow Local**を選択して `unknowns-workflow` をインストールすることもできます。インストール後に新しいタスクを開始すると、Codex がバンドルされたスキルを検出します。必要に応じて以下のように明示的に呼び出してください。

```text
$finding-unknowns
```

ローカルのチェックアウトを更新し、キャッシュされたプラグインを再インストールするには：

```bash
git pull
codex plugin marketplace upgrade unknowns-workflow-local
codex plugin add unknowns-workflow@unknowns-workflow-local
```

チェックアウト先を移動した場合は、古いマーケットプレイス登録を削除し、新しいリポジトリパスを追加してから再インストールしてください。

```bash
codex plugin marketplace remove unknowns-workflow-local
codex plugin marketplace add /new/path/to/unknowns-workflow
codex plugin add unknowns-workflow@unknowns-workflow-local
```

※このマーケットプレイスはローカル専用です。プラグインを公開したり、パブリックなプラグインディレクトリに登録したりすることはありません。

### スキルの直接インストール

より軽量なセットアップとして、`skills/` から任意のスキルフォルダをエージェントのスキルディレクトリにコピーするか、スキルのテキストをワークフローのプロンプト内に直接参照させることも可能です。

名前付きフォルダ構成を使用するエージェントスキルディレクトリの場合、構造は以下のようになります。

```text
skills/
  finding-unknowns/
    SKILL.md
```

## コピペ用プロンプト

スキルを事前にインストールせずに、エージェントにこのワークフローを適用させたい場合は、以下のプロンプトを使用してください（日本語または英語のいずれかで指示できます）。

```text
Before implementing, run an unknowns pass.

Classify the work into:
- Known Knowns
- Known Unknowns
- Unknown Knowns
- Unknown Unknowns

Declare familiarity as new, partial, or known. If the area is unfamiliar,
teach me the likely blindspots before planning. If the success criteria are
implicit, give me a few concrete options to react to before editing code. If
named decisions remain, ask only the questions that would change architecture,
scope, or user-visible behavior.

During implementation, keep implementation notes. If the real codebase forces
you to deviate from the plan, choose the conservative option and log:
- Expected
- Found
- Chosen conservative option
- Why conservative
- Follow-up needed
```

（日本語訳の指示例：）
```text
実装に入る前に、unknowns パスを実行してください。

作業内容を以下に分類してください：
- Known Knowns（既知の既知）
- Known Unknowns（既知の未知）
- Unknown Knowns（未知の既知）
- Unknown Unknowns（未知の未知）

この領域への習熟度（familiarity）を new（新規）、partial（一部知っている）、known（既知）のいずれかで宣言してください。
もし不慣れな領域（new）であれば、計画を立てる前に起こりうるブラインドスポット（盲点）を教えてください。
もし成功基準が暗黙的であれば、コードを修正する前に、私が判断できるような具体的な選択肢をいくつか提示してください。
未決の決定事項が残っている場合は、アーキテクチャ、スコープ、またはユーザーに見える挙動を変更するような重要な質問のみを厳選して聞いてください。

実装中は、implementation-notes.md（実装ノート）を記録してください。もし実際のコードベースの状況によって計画から逸脱（deviate）せざるを得なくなった場合は、保守的な選択肢を採用し、以下を記録してください：
- Expected（想定していた挙動・設計）
- Found（実際に発見したコードベースの状況）
- Chosen conservative option（採用した保守的な選択肢）
- Why conservative（なぜそれが保守的と言えるのか）
- Follow-up needed（必要なフォローアップ・今後の課題）
```

## ひとことで言うと

`unknowns-workflow` は、AIに実装させる前に「何を知らないまま進もうとしているのか」を見つけるための道具です。

AIを賢くするというより、**AIに渡す前提を賢くする**ためのワークフローです。
