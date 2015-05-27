# Spillo for Alfred

An Alfred workflow that lets you search your bookmarks in [Spillo](http://bananafishsoftware.com/products/spillo).

You can download the latest version of the workflow from [here](https://github.com/ddeville/spillo-alfred/releases/latest) or from [Packal](http://www.packal.org/workflow/spillo).

## Usage

You can invoke the workflow by using the `spl` command in Alfred.

You can search in two different ways:

### Global

Just type some text after the `spl` command and Spillo will search against the title, URL, description and tags of your bookmarks. Simple.

```
spl objective-c atomics
```

### Specific

If you want more control, you can specify various parameters in your search. The following parameters are supported:

- `-n`/`--name`: The name of the bookmark (text)
- `-u`/`--url`: The URL of the bookmark (text)
- `-d`/`--desc`: The description of the bookmark (text)
- `-t`/`--tags`: The tags of the bookmark (text, separated by space)
- `-un`/`--unread`: Whether the bookmark is unread (`1` or `0`, `true` or `false`, `yes` or `no`)
- `-pu`/`--public`: Whether the bookmark is public (`1` or `0`, `true` or `false`, `yes` or `no`)

You can use multiple parameters at the same time.

```
spl -n nullability -t objc swift -un 1
```

#### Unread

You can also see a list of your unread bookmarks by using the `splunread` command in Alfred.

## Hotkeys

The workflow has some hotkeys setup that you can use to start a search of view your unread bookmarks. These hotkeys are left blank by default but you can easily set them up by editing them in the workflow.

## Actions

When you have found the bookmark you are looking for, you can open it in your default browser. Just hit Return or click on the bookmark in the Alfred search results.

Alternatively, you can open the bookmark in the background by holding the option key.

You can also open the bookmark in Spillo by holding the command key.

## Notes

Note that Spillo needs to be installed and authenticated on your machine for the workflow to work.
