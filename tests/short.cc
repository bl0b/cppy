typedef struct
{
    int __count;
    union
    {
        unsigned int __wch;
        char __wchb[4];
    } __value;
} __mbstate_t;
typedef __mbstate_t mbstate_t;
namespace std __attribute__ ((__visibility__ ("default"))) {
    using ::mbstate_t;
}
typedef long int ptrdiff_t;
typedef long unsigned int size_t;
namespace std __attribute__ ((__visibility__ ("default"))) {
    using ::ptrdiff_t;
    using ::size_t;
}
namespace std __attribute__ ((__visibility__ ("default"))) {
    template<typename _Alloc>
        class allocator;
    template<class _CharT>
        struct char_traits;
    template<typename _CharT, typename _Traits = char_traits<_CharT>,
        typename _Alloc = allocator<_CharT> >
            class basic_string;
    template<> struct char_traits<char>;
    typedef basic_string<char> string;
    template<> struct char_traits<wchar_t>;
    typedef basic_string<wchar_t> wstring;
}
struct _IO_FILE;
typedef struct _IO_FILE FILE;
typedef struct _IO_FILE __FILE;
typedef __builtin_va_list __gnuc_va_list;
typedef unsigned int wint_t;
extern "C" {
    struct tm;
    extern wchar_t *wcscpy (wchar_t *__restrict __dest,
            __const wchar_t *__restrict __src) throw ();
    extern wchar_t *wcsncpy (wchar_t *__restrict __dest,
            __const wchar_t *__restrict __src, size_t __n)
        throw ();
    extern wchar_t *wcscat (wchar_t *__restrict __dest,
            __const wchar_t *__restrict __src) throw ();
    extern wchar_t *wcsncat (wchar_t *__restrict __dest,
            __const wchar_t *__restrict __src, size_t __n)
        throw ();
    extern int wcscmp (__const wchar_t *__s1, __const wchar_t *__s2)
        throw () __attribute__ ((__pure__));
    extern int wcsncmp (__const wchar_t *__s1, __const wchar_t *__s2, size_t __n)
        throw () __attribute__ ((__pure__));
    extern int wcscasecmp (__const wchar_t *__s1, __const wchar_t *__s2) throw ();
    extern int wcsncasecmp (__const wchar_t *__s1, __const wchar_t *__s2,
            size_t __n) throw ();
    typedef struct __locale_struct
    {
        struct locale_data *__locales[13];
        const unsigned short int *__ctype_b;
        const int *__ctype_tolower;
        const int *__ctype_toupper;
        const char *__names[13];
    } *__locale_t;
    typedef __locale_t locale_t;
    extern int wcscasecmp_l (__const wchar_t *__s1, __const wchar_t *__s2,
            __locale_t __loc) throw ();
    extern int wcsncasecmp_l (__const wchar_t *__s1, __const wchar_t *__s2,
            size_t __n, __locale_t __loc) throw ();
    extern int wcscoll (__const wchar_t *__s1, __const wchar_t *__s2) throw ();
    extern size_t wcsxfrm (wchar_t *__restrict __s1,
            __const wchar_t *__restrict __s2, size_t __n) throw ();
    extern int wcscoll_l (__const wchar_t *__s1, __const wchar_t *__s2,
            __locale_t __loc) throw ();
    extern size_t wcsxfrm_l (wchar_t *__s1, __const wchar_t *__s2,
            size_t __n, __locale_t __loc) throw ();
    extern wchar_t *wcsdup (__const wchar_t *__s) throw () __attribute__ ((__malloc__));
    extern "C++" wchar_t *wcschr (wchar_t *__wcs, wchar_t __wc)
        throw () __asm ("wcschr") __attribute__ ((__pure__));
    extern "C++" __const wchar_t *wcschr (__const wchar_t *__wcs, wchar_t __wc)
        throw () __asm ("wcschr") __attribute__ ((__pure__));
    extern "C++" wchar_t *wcsrchr (wchar_t *__wcs, wchar_t __wc)
        throw () __asm ("wcsrchr") __attribute__ ((__pure__));
    extern "C++" __const wchar_t *wcsrchr (__const wchar_t *__wcs, wchar_t __wc)
        throw () __asm ("wcsrchr") __attribute__ ((__pure__));
    extern wchar_t *wcschrnul (__const wchar_t *__s, wchar_t __wc)
        throw () __attribute__ ((__pure__));
    extern size_t wcscspn (__const wchar_t *__wcs, __const wchar_t *__reject)
        throw () __attribute__ ((__pure__));
    extern size_t wcsspn (__const wchar_t *__wcs, __const wchar_t *__accept)
        throw () __attribute__ ((__pure__));
    extern "C++" wchar_t *wcspbrk (wchar_t *__wcs, __const wchar_t *__accept)
        throw () __asm ("wcspbrk") __attribute__ ((__pure__));
    extern "C++" __const wchar_t *wcspbrk (__const wchar_t *__wcs,
            __const wchar_t *__accept)
        throw () __asm ("wcspbrk") __attribute__ ((__pure__));
    extern "C++" wchar_t *wcsstr (wchar_t *__haystack, __const wchar_t *__needle)
        throw () __asm ("wcsstr") __attribute__ ((__pure__));
    extern "C++" __const wchar_t *wcsstr (__const wchar_t *__haystack,
            __const wchar_t *__needle)
        throw () __asm ("wcsstr") __attribute__ ((__pure__));
    extern wchar_t *wcstok (wchar_t *__restrict __s,
            __const wchar_t *__restrict __delim,
            wchar_t **__restrict __ptr) throw ();
    extern size_t wcslen (__const wchar_t *__s) throw () __attribute__ ((__pure__));
    extern "C++" wchar_t *wcswcs (wchar_t *__haystack, __const wchar_t *__needle)
        throw () __asm ("wcswcs") __attribute__ ((__pure__));
    extern "C++" __const wchar_t *wcswcs (__const wchar_t *__haystack,
            __const wchar_t *__needle)
        throw () __asm ("wcswcs") __attribute__ ((__pure__));
    extern size_t wcsnlen (__const wchar_t *__s, size_t __maxlen)
        throw () __attribute__ ((__pure__));
    extern "C++" wchar_t *wmemchr (wchar_t *__s, wchar_t __c, size_t __n)
        throw () __asm ("wmemchr") __attribute__ ((__pure__));
    extern "C++" __const wchar_t *wmemchr (__const wchar_t *__s, wchar_t __c,
            size_t __n)
        throw () __asm ("wmemchr") __attribute__ ((__pure__));
    extern int wmemcmp (__const wchar_t *__restrict __s1,
            __const wchar_t *__restrict __s2, size_t __n)
        throw () __attribute__ ((__pure__));
    extern wchar_t *wmemcpy (wchar_t *__restrict __s1,
            __const wchar_t *__restrict __s2, size_t __n) throw ();
    extern wchar_t *wmemmove (wchar_t *__s1, __const wchar_t *__s2, size_t __n)
        throw ();
    extern wchar_t *wmemset (wchar_t *__s, wchar_t __c, size_t __n) throw ();
    extern wchar_t *wmempcpy (wchar_t *__restrict __s1,
            __const wchar_t *__restrict __s2, size_t __n)
        throw ();
    extern wint_t btowc (int __c) throw ();
    extern int wctob (wint_t __c) throw ();
    extern int mbsinit (__const mbstate_t *__ps) throw () __attribute__ ((__pure__));
    extern size_t mbrtowc (wchar_t *__restrict __pwc,
            __const char *__restrict __s, size_t __n,
            mbstate_t *__p) throw ();
    extern size_t wcrtomb (char *__restrict __s, wchar_t __wc,
            mbstate_t *__restrict __ps) throw ();
    extern size_t __mbrlen (__const char *__restrict __s, size_t __n,
            mbstate_t *__restrict __ps) throw ();
    extern size_t mbrlen (__const char *__restrict __s, size_t __n,
            mbstate_t *__restrict __ps) throw ();
    extern size_t mbsrtowcs (wchar_t *__restrict __dst,
            __const char **__restrict __src, size_t __len,
            mbstate_t *__restrict __ps) throw ();
    extern size_t wcsrtombs (char *__restrict __dst,
            __const wchar_t **__restrict __src, size_t __len,
            mbstate_t *__restrict __ps) throw ();
    extern size_t mbsnrtowcs (wchar_t *__restrict __dst,
            __const char **__restrict __src, size_t __nmc,
            size_t __len, mbstate_t *__restrict __ps) throw ();
    extern size_t wcsnrtombs (char *__restrict __dst,
            __const wchar_t **__restrict __src,
            size_t __nwc, size_t __len,
            mbstate_t *__restrict __ps) throw ();
    extern int wcwidth (wchar_t __c) throw ();
    extern int wcswidth (__const wchar_t *__s, size_t __n) throw ();
    extern double wcstod (__const wchar_t *__restrict __nptr,
            wchar_t **__restrict __endptr) throw ();
    extern float wcstof (__const wchar_t *__restrict __nptr,
            wchar_t **__restrict __endptr) throw ();
    extern long double wcstold (__const wchar_t *__restrict __nptr,
            wchar_t **__restrict __endptr) throw ();
    extern long int wcstol (__const wchar_t *__restrict __nptr,
            wchar_t **__restrict __endptr, int __base) throw ();
    extern unsigned long int wcstoul (__const wchar_t *__restrict __nptr,
            wchar_t **__restrict __endptr, int __base)
        throw ();
    __extension__
        extern long long int wcstoll (__const wchar_t *__restrict __nptr,
                wchar_t **__restrict __endptr, int __base)
        throw ();
    __extension__
        extern unsigned long long int wcstoull (__const wchar_t *__restrict __nptr,
                wchar_t **__restrict __endptr,
                int __base) throw ();
    __extension__
        extern long long int wcstoq (__const wchar_t *__restrict __nptr,
                wchar_t **__restrict __endptr, int __base)
        throw ();
    __extension__
        extern unsigned long long int wcstouq (__const wchar_t *__restrict __nptr,
                wchar_t **__restrict __endptr,
                int __base) throw ();
    extern long int wcstol_l (__const wchar_t *__restrict __nptr,
            wchar_t **__restrict __endptr, int __base,
            __locale_t __loc) throw ();
    extern unsigned long int wcstoul_l (__const wchar_t *__restrict __nptr,
            wchar_t **__restrict __endptr,
            int __base, __locale_t __loc) throw ();
    __extension__
        extern long long int wcstoll_l (__const wchar_t *__restrict __nptr,
                wchar_t **__restrict __endptr,
                int __base, __locale_t __loc) throw ();
    __extension__
        extern unsigned long long int wcstoull_l (__const wchar_t *__restrict __nptr,
                wchar_t **__restrict __endptr,
                int __base, __locale_t __loc)
        throw ();
    extern double wcstod_l (__const wchar_t *__restrict __nptr,
            wchar_t **__restrict __endptr, __locale_t __loc)
        throw ();
    extern float wcstof_l (__const wchar_t *__restrict __nptr,
            wchar_t **__restrict __endptr, __locale_t __loc)
        throw ();
    extern long double wcstold_l (__const wchar_t *__restrict __nptr,
            wchar_t **__restrict __endptr,
            __locale_t __loc) throw ();
    extern wchar_t *wcpcpy (wchar_t *__dest, __const wchar_t *__src) throw ();
    extern wchar_t *wcpncpy (wchar_t *__dest, __const wchar_t *__src, size_t __n)
        throw ();
    extern __FILE *open_wmemstream (wchar_t **__bufloc, size_t *__sizeloc) throw ();
    extern int fwide (__FILE *__fp, int __mode) throw ();
    extern int fwprintf (__FILE *__restrict __stream,
            __const wchar_t *__restrict __format, ...)
        ;
    extern int wprintf (__const wchar_t *__restrict __format, ...)
        ;
    extern int swprintf (wchar_t *__restrict __s, size_t __n,
            __const wchar_t *__restrict __format, ...)
        throw () ;
    extern int vfwprintf (__FILE *__restrict __s,
            __const wchar_t *__restrict __format,
            __gnuc_va_list __arg)
        ;
    extern int vwprintf (__const wchar_t *__restrict __format,
            __gnuc_va_list __arg)
        ;
    extern int vswprintf (wchar_t *__restrict __s, size_t __n,
            __const wchar_t *__restrict __format,
            __gnuc_va_list __arg)
        throw () ;
    extern int fwscanf (__FILE *__restrict __stream,
            __const wchar_t *__restrict __format, ...)
        ;
    extern int wscanf (__const wchar_t *__restrict __format, ...)
        ;
    extern int swscanf (__const wchar_t *__restrict __s,
            __const wchar_t *__restrict __format, ...)
        throw () ;
    extern int vfwscanf (__FILE *__restrict __s,
            __const wchar_t *__restrict __format,
            __gnuc_va_list __arg)
        ;
    extern int vwscanf (__const wchar_t *__restrict __format,
            __gnuc_va_list __arg)
        ;
    extern int vswscanf (__const wchar_t *__restrict __s,
            __const wchar_t *__restrict __format,
            __gnuc_va_list __arg)
        throw () ;
    extern wint_t fgetwc (__FILE *__stream);
    extern wint_t getwc (__FILE *__stream);
    extern wint_t getwchar (void);
    extern wint_t fputwc (wchar_t __wc, __FILE *__stream);
    extern wint_t putwc (wchar_t __wc, __FILE *__stream);
    extern wint_t putwchar (wchar_t __wc);
    extern wchar_t *fgetws (wchar_t *__restrict __ws, int __n,
            __FILE *__restrict __stream);
    extern int fputws (__const wchar_t *__restrict __ws,
            __FILE *__restrict __stream);
    extern wint_t ungetwc (wint_t __wc, __FILE *__stream);
    extern wint_t getwc_unlocked (__FILE *__stream);
    extern wint_t getwchar_unlocked (void);
    extern wint_t fgetwc_unlocked (__FILE *__stream);
    extern wint_t fputwc_unlocked (wchar_t __wc, __FILE *__stream);
    extern wint_t putwc_unlocked (wchar_t __wc, __FILE *__stream);
    extern wint_t putwchar_unlocked (wchar_t __wc);
    extern wchar_t *fgetws_unlocked (wchar_t *__restrict __ws, int __n,
            __FILE *__restrict __stream);
    extern int fputws_unlocked (__const wchar_t *__restrict __ws,
            __FILE *__restrict __stream);
    extern size_t wcsftime (wchar_t *__restrict __s, size_t __maxsize,
            __const wchar_t *__restrict __format,
            __const struct tm *__restrict __tp) throw ();
    extern size_t wcsftime_l (wchar_t *__restrict __s, size_t __maxsize,
            __const wchar_t *__restrict __format,
            __const struct tm *__restrict __tp,
            __locale_t __loc) throw ();
}
namespace std __attribute__ ((__visibility__ ("default"))) {
    using ::wint_t;
    using ::btowc;
    using ::fgetwc;
    using ::fgetws;
    using ::fputwc;
    using ::fputws;
    using ::fwide;
    using ::fwprintf;
    using ::fwscanf;
    using ::getwc;
    using ::getwchar;
    using ::mbrlen;
    using ::mbrtowc;
    using ::mbsinit;
    using ::mbsrtowcs;
    using ::putwc;
    using ::putwchar;
    using ::swprintf;
    using ::swscanf;
    using ::ungetwc;
    using ::vfwprintf;
    using ::vfwscanf;
    using ::vswprintf;
    using ::vswscanf;
    using ::vwprintf;
    using ::vwscanf;
    using ::wcrtomb;
    using ::wcscat;
    using ::wcscmp;
    using ::wcscoll;
    using ::wcscpy;
    using ::wcscspn;
    using ::wcsftime;
    using ::wcslen;
    using ::wcsncat;
    using ::wcsncmp;
    using ::wcsncpy;
    using ::wcsrtombs;
    using ::wcsspn;
    using ::wcstod;
    using ::wcstof;
    using ::wcstok;
    using ::wcstol;
    using ::wcstoul;
    using ::wcsxfrm;
    using ::wctob;
    using ::wmemcmp;
    using ::wmemcpy;
    using ::wmemmove;
    using ::wmemset;
    using ::wprintf;
    using ::wscanf;
    using ::wcschr;
    using ::wcspbrk;
    using ::wcsrchr;
    using ::wcsstr;
    using ::wmemchr;
}
namespace __gnu_cxx __attribute__ ((__visibility__ ("default"))) {
    using ::wcstold;
    using ::wcstoll;
    using ::wcstoull;
}
namespace std __attribute__ ((__visibility__ ("default"))) {
    using ::__gnu_cxx::wcstold;
    using ::__gnu_cxx::wcstoll;
    using ::__gnu_cxx::wcstoull;
}
